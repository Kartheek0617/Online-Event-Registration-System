from typing import List, Optional, Tuple
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.models.event import Event, EventStatus
from backend.app.models.user import User, UserRole
from backend.app.models.registration import Registration, RegistrationStatus
from backend.app.schemas.event import EventCreate, EventUpdate
from backend.app.services.audit_service import AuditService


class EventService:
    @staticmethod
    def get_event_counts(db: Session, event_id: int) -> int:
        """Count confirmed registrations for an event."""
        return db.query(func.count(Registration.id)).filter(
            Registration.event_id == event_id,
            Registration.status == RegistrationStatus.CONFIRMED
        ).scalar() or 0

    @staticmethod
    def list_events(
        db: Session,
        search: Optional[str] = None,
        category: Optional[str] = None,
        status_filter: Optional[EventStatus] = None
    ) -> List[dict]:
        """Fetch events with search, category filtering, and capacity metrics."""
        query = db.query(Event, User.name.label("organizer_name")).join(User, Event.organizer_id == User.id)

        if search:
            search_term = f"%{search.strip()}%"
            query = query.filter(
                (Event.title.ilike(search_term)) |
                (Event.description.ilike(search_term)) |
                (Event.venue.ilike(search_term))
            )
        if category:
            query = query.filter(Event.category.ilike(category.strip()))
        if status_filter:
            query = query.filter(Event.status == status_filter)

        results = query.order_by(Event.event_date.asc(), Event.start_time.asc()).all()

        events_out = []
        for event, organizer_name in results:
            reg_count = EventService.get_event_counts(db, event.id)
            avail = max(0, event.participant_limit - reg_count)
            events_out.append({
                "id": event.id,
                "organizer_id": event.organizer_id,
                "title": event.title,
                "description": event.description,
                "category": event.category,
                "venue": event.venue,
                "event_date": event.event_date,
                "start_time": event.start_time,
                "end_time": event.end_time,
                "participant_limit": event.participant_limit,
                "registration_deadline": event.registration_deadline,
                "status": event.status,
                "registered_count": reg_count,
                "available_seats": avail,
                "organizer_name": organizer_name,
                "created_at": event.created_at,
                "updated_at": event.updated_at
            })
        return events_out

    @staticmethod
    def get_event_detail(
        db: Session,
        event_id: int,
        current_user: Optional[User] = None
    ) -> dict:
        """Fetch complete event details with registration status for the user."""
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event with ID {event_id} not found."
            )

        organizer = db.query(User).filter(User.id == event.organizer_id).first()
        reg_count = EventService.get_event_counts(db, event.id)
        avail = max(0, event.participant_limit - reg_count)

        is_registered = False
        user_reg_id = None

        if current_user and current_user.role == UserRole.STUDENT:
            reg = db.query(Registration).filter(
                Registration.event_id == event.id,
                Registration.student_id == current_user.id,
                Registration.status == RegistrationStatus.CONFIRMED
            ).first()
            if reg:
                is_registered = True
                user_reg_id = reg.id

        return {
            "id": event.id,
            "organizer_id": event.organizer_id,
            "title": event.title,
            "description": event.description,
            "category": event.category,
            "venue": event.venue,
            "event_date": event.event_date,
            "start_time": event.start_time,
            "end_time": event.end_time,
            "participant_limit": event.participant_limit,
            "registration_deadline": event.registration_deadline,
            "status": event.status,
            "registered_count": reg_count,
            "available_seats": avail,
            "organizer_name": organizer.name if organizer else "Unknown",
            "created_at": event.created_at,
            "updated_at": event.updated_at,
            "is_registered_by_user": is_registered,
            "user_registration_id": user_reg_id
        }

    @staticmethod
    def create_event(
        db: Session,
        event_in: EventCreate,
        current_user: User,
        client_ip: Optional[str] = None
    ) -> Event:
        """Create a new event associated with the faculty organizer."""
        new_event = Event(
            organizer_id=current_user.id,
            title=event_in.title,
            description=event_in.description,
            category=event_in.category,
            venue=event_in.venue,
            event_date=event_in.event_date,
            start_time=event_in.start_time,
            end_time=event_in.end_time,
            participant_limit=event_in.participant_limit,
            registration_deadline=event_in.registration_deadline,
            status=EventStatus.OPEN
        )
        db.add(new_event)
        db.commit()
        db.refresh(new_event)

        AuditService.log_event(
            db=db,
            action="EVENT_CREATED",
            entity_type="EVENT",
            actor_id=current_user.id,
            entity_id=new_event.id,
            source_ip=client_ip,
            result="SUCCESS",
            metadata={"title": new_event.title, "limit": new_event.participant_limit}
        )
        return new_event

    @staticmethod
    def update_event(
        db: Session,
        event_id: int,
        event_in: EventUpdate,
        current_user: User,
        client_ip: Optional[str] = None
    ) -> Event:
        """Update event details with strict object-level authorization."""
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event with ID {event_id} not found."
            )

        # Object-level authorization: only the creator faculty or an admin can update
        if event.organizer_id != current_user.id and current_user.role != UserRole.ADMIN:
            AuditService.log_event(
                db=db,
                action="UNAUTHORIZED_EVENT_UPDATE_ATTEMPT",
                entity_type="EVENT",
                actor_id=current_user.id,
                entity_id=event_id,
                source_ip=client_ip,
                result="DENIED"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden: You cannot modify an event organized by another faculty member."
            )

        update_data = event_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(event, key, value)

        db.commit()
        db.refresh(event)

        AuditService.log_event(
            db=db,
            action="EVENT_UPDATED",
            entity_type="EVENT",
            actor_id=current_user.id,
            entity_id=event.id,
            source_ip=client_ip,
            result="SUCCESS"
        )
        return event

    @staticmethod
    def close_event(
        db: Session,
        event_id: int,
        current_user: User,
        client_ip: Optional[str] = None
    ) -> Event:
        """Close event registration with object-level authorization check."""
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event with ID {event_id} not found."
            )

        # Object-level authorization check
        if event.organizer_id != current_user.id and current_user.role != UserRole.ADMIN:
            AuditService.log_event(
                db=db,
                action="UNAUTHORIZED_EVENT_CLOSE_ATTEMPT",
                entity_type="EVENT",
                actor_id=current_user.id,
                entity_id=event_id,
                source_ip=client_ip,
                result="DENIED"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden: You cannot close an event organized by another faculty member."
            )

        event.status = EventStatus.CLOSED
        db.commit()
        db.refresh(event)

        AuditService.log_event(
            db=db,
            action="EVENT_CLOSED",
            entity_type="EVENT",
            actor_id=current_user.id,
            entity_id=event.id,
            source_ip=client_ip,
            result="SUCCESS"
        )
        return event
