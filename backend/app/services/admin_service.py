from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status
from backend.app.models.user import User, UserRole
from backend.app.models.event import Event, EventStatus
from backend.app.models.registration import Registration, RegistrationStatus
from backend.app.models.audit_log import AuditLog
from backend.app.services.audit_service import AuditService


class AdminService:
    @staticmethod
    def list_users(db: Session) -> List[User]:
        """Fetch all system users."""
        return db.query(User).order_by(User.id.asc()).all()

    @staticmethod
    def update_user_role(
        db: Session,
        user_id: int,
        new_role: UserRole,
        admin_user: User,
        client_ip: Optional[str] = None
    ) -> User:
        """Update role of an existing user with audit tracking."""
        target_user = db.query(User).filter(User.id == user_id).first()
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found."
            )

        old_role = target_user.role
        target_user.role = new_role
        db.commit()
        db.refresh(target_user)

        AuditService.log_event(
            db=db,
            action="USER_ROLE_CHANGED",
            entity_type="USER",
            actor_id=admin_user.id,
            entity_id=target_user.id,
            source_ip=client_ip,
            result="SUCCESS",
            metadata={"old_role": old_role.value, "new_role": new_role.value}
        )
        return target_user

    @staticmethod
    def get_system_stats(db: Session) -> dict:
        """Aggregate high-level operational statistics."""
        total_users = db.query(func.count(User.id)).scalar() or 0
        total_students = db.query(func.count(User.id)).filter(User.role == UserRole.STUDENT).scalar() or 0
        total_faculty = db.query(func.count(User.id)).filter(User.role == UserRole.FACULTY).scalar() or 0
        total_events = db.query(func.count(Event.id)).scalar() or 0
        active_events = db.query(func.count(Event.id)).filter(Event.status == EventStatus.OPEN).scalar() or 0
        total_regs = db.query(func.count(Registration.id)).scalar() or 0
        confirmed_regs = db.query(func.count(Registration.id)).filter(Registration.status == RegistrationStatus.CONFIRMED).scalar() or 0
        total_audits = db.query(func.count(AuditLog.id)).scalar() or 0

        return {
            "total_users": total_users,
            "total_students": total_students,
            "total_faculty": total_faculty,
            "total_events": total_events,
            "active_events": active_events,
            "total_registrations": total_regs,
            "confirmed_registrations": confirmed_regs,
            "total_audit_logs": total_audits
        }

    @staticmethod
    def list_audit_logs(db: Session, limit: int = 100) -> List[dict]:
        """Fetch audit log entries joined with actor metadata."""
        records = db.query(
            AuditLog, User.name.label("actor_name"), User.email.label("actor_email")
        ).outerjoin(
            User, AuditLog.actor_id == User.id
        ).order_by(AuditLog.timestamp.desc()).limit(limit).all()

        logs_out = []
        for log, actor_name, actor_email in records:
            logs_out.append({
                "id": log.id,
                "actor_id": log.actor_id,
                "actor_name": actor_name,
                "actor_email": actor_email,
                "action": log.action,
                "entity_type": log.entity_type,
                "entity_id": log.entity_id,
                "timestamp": log.timestamp,
                "source_ip": log.source_ip,
                "result": log.result,
                "metadata_json": log.metadata_json
            })
        return logs_out
