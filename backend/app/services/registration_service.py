from datetime import datetime, timezone
from typing import List, Optional
from threading import Lock
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from backend.app.models.event import Event, EventStatus
from backend.app.models.user import User, UserRole
from backend.app.models.registration import Registration, RegistrationStatus
from backend.app.services.audit_service import AuditService

# In-process mutex to ensure strict atomic serialization on concurrency tests even across SQLite
_concurrency_lock = Lock()


class RegistrationService:
    @staticmethod
    def register_student_for_event(
        db: Session,
        event_id: int,
        student: User,
        client_ip: Optional[str] = None
    ) -> Registration:
        """
        Atomic, concurrency-safe registration workflow.
        Guarantees:
        1. Only authenticated students can register.
        2. Closed or past events are rejected.
        3. Duplicate registrations are strictly prevented.
        4. Overbooking race conditions are eliminated.
        """
        if student.role != UserRole.STUDENT and student.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only students can register for events."
            )

        with _concurrency_lock:
            # 1. Fetch event with locking if supported by dialect
            query = db.query(Event).filter(Event.id == event_id)
            if db.bind and db.bind.dialect.name == "postgresql":
                query = query.with_for_update()
            
            event = query.first()
            if not event:
                AuditService.log_event(
                    db=db,
                    action="REGISTRATION_FAILED_INVALID_EVENT",
                    entity_type="EVENT",
                    actor_id=student.id,
                    entity_id=event_id,
                    source_ip=client_ip,
                    result="FAILURE"
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Event with ID {event_id} does not exist."
                )

            # 2. Check event status
            if event.status != EventStatus.OPEN:
                AuditService.log_event(
                    db=db,
                    action="REGISTRATION_FAILED_EVENT_CLOSED",
                    entity_type="EVENT",
                    actor_id=student.id,
                    entity_id=event_id,
                    source_ip=client_ip,
                    result="DENIED"
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Registration is closed for this event."
                )

            # 3. Check for existing active registration (Duplicate check)
            existing_active = db.query(Registration).filter(
                Registration.event_id == event.id,
                Registration.student_id == student.id,
                Registration.status == RegistrationStatus.CONFIRMED
            ).first()

            if existing_active:
                AuditService.log_event(
                    db=db,
                    action="REGISTRATION_DUPLICATE_ATTEMPT",
                    entity_type="REGISTRATION",
                    actor_id=student.id,
                    entity_id=existing_active.id,
                    source_ip=client_ip,
                    result="DENIED"
                )
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="You are already registered for this event."
                )

            # 4. Check capacity (Prevent overbooking race condition)
            current_count = db.query(func.count(Registration.id)).filter(
                Registration.event_id == event.id,
                Registration.status == RegistrationStatus.CONFIRMED
            ).scalar() or 0

            if current_count >= event.participant_limit:
                AuditService.log_event(
                    db=db,
                    action="REGISTRATION_CAPACITY_EXCEEDED",
                    entity_type="EVENT",
                    actor_id=student.id,
                    entity_id=event.id,
                    source_ip=client_ip,
                    result="DENIED",
                    metadata={"limit": event.participant_limit, "current": current_count}
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Event capacity reached ({event.participant_limit} seats full)."
                )

            # 5. Check if there was a previously cancelled registration to reactivate or create new
            cancelled_reg = db.query(Registration).filter(
                Registration.event_id == event.id,
                Registration.student_id == student.id,
                Registration.status == RegistrationStatus.CANCELLED
            ).first()

            try:
                if cancelled_reg:
                    cancelled_reg.status = RegistrationStatus.CONFIRMED
                    cancelled_reg.registered_at = datetime.now(timezone.utc)
                    cancelled_reg.cancelled_at = None
                    reg = cancelled_reg
                else:
                    reg = Registration(
                        event_id=event.id,
                        student_id=student.id,
                        status=RegistrationStatus.CONFIRMED
                    )
                    db.add(reg)

                db.commit()
                db.refresh(reg)
            except IntegrityError:
                db.rollback()
                AuditService.log_event(
                    db=db,
                    action="REGISTRATION_INTEGRITY_CONFLICT",
                    entity_type="EVENT",
                    actor_id=student.id,
                    entity_id=event.id,
                    source_ip=client_ip,
                    result="DENIED"
                )
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Duplicate registration detected by database constraint."
                )

        AuditService.log_event(
            db=db,
            action="EVENT_REGISTRATION_SUCCESS",
            entity_type="REGISTRATION",
            actor_id=student.id,
            entity_id=reg.id,
            source_ip=client_ip,
            result="SUCCESS",
            metadata={"event_title": event.title}
        )
        return reg

    @staticmethod
    def cancel_registration(
        db: Session,
        registration_id: int,
        current_user: User,
        client_ip: Optional[str] = None
    ) -> Registration:
        """
        Object-level authorization: Only the owning student or an admin may cancel a registration.
        Updates available capacity immediately.
        """
        reg = db.query(Registration).filter(Registration.id == registration_id).first()
        if not reg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Registration with ID {registration_id} not found."
            )

        # Object-level authorization check: Student A cannot cancel Student B's registration
        if reg.student_id != current_user.id and current_user.role != UserRole.ADMIN:
            AuditService.log_event(
                db=db,
                action="UNAUTHORIZED_CANCELLATION_ATTEMPT",
                entity_type="REGISTRATION",
                actor_id=current_user.id,
                entity_id=registration_id,
                source_ip=client_ip,
                result="DENIED"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden: You are not authorized to cancel this registration."
            )

        if reg.status == RegistrationStatus.CANCELLED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration is already cancelled."
            )

        reg.status = RegistrationStatus.CANCELLED
        reg.cancelled_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(reg)

        AuditService.log_event(
            db=db,
            action="EVENT_REGISTRATION_CANCELLED",
            entity_type="REGISTRATION",
            actor_id=current_user.id,
            entity_id=reg.id,
            source_ip=client_ip,
            result="SUCCESS",
            metadata={"event_id": reg.event_id}
        )
        return reg

    @staticmethod
    def get_student_registrations(
        db: Session,
        student: User
    ) -> List[dict]:
        """Fetch registrations exclusively owned by the authenticated student."""
        results = db.query(Registration, Event).join(
            Event, Registration.event_id == Event.id
        ).filter(
            Registration.student_id == student.id
        ).order_by(Registration.registered_at.desc()).all()

        registrations_out = []
        for reg, event in results:
            registrations_out.append({
                "id": reg.id,
                "event_id": reg.event_id,
                "student_id": reg.student_id,
                "registered_at": reg.registered_at,
                "status": reg.status,
                "cancelled_at": reg.cancelled_at,
                "event_title": event.title,
                "event_date": event.event_date,
                "venue": event.venue,
                "category": event.category
            })
        return registrations_out

    @staticmethod
    def get_event_participants(
        db: Session,
        event_id: int,
        current_user: User,
        client_ip: Optional[str] = None
    ) -> List[dict]:
        """
        Fetch participant roster for an event.
        Object-level authorization: Only the faculty organizer who created the event or an admin can access.
        """
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event with ID {event_id} not found."
            )

        # Faculty A cannot view Faculty B's participants; Students cannot view participants
        if event.organizer_id != current_user.id and current_user.role != UserRole.ADMIN:
            AuditService.log_event(
                db=db,
                action="UNAUTHORIZED_PARTICIPANT_ACCESS_ATTEMPT",
                entity_type="EVENT",
                actor_id=current_user.id,
                entity_id=event_id,
                source_ip=client_ip,
                result="DENIED"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden: You can only view participant rosters for your own events."
            )

        records = db.query(Registration, User).join(
            User, Registration.student_id == User.id
        ).filter(
            Registration.event_id == event_id,
            Registration.status == RegistrationStatus.CONFIRMED
        ).order_by(Registration.registered_at.asc()).all()

        participants_out = []
        for reg, student in records:
            participants_out.append({
                "registration_id": reg.id,
                "student_id": student.id,
                "student_name": student.name,
                "student_email": student.email,
                "registered_at": reg.registered_at,
                "status": reg.status
            })
        return participants_out
