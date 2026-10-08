from typing import List
from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.models.user import User, UserRole
from backend.app.schemas.user import UserOut, UserRoleUpdate
from backend.app.schemas.event import EventOut
from backend.app.schemas.audit_log import AuditLogOut, SystemStatsOut
from backend.app.services.admin_service import AdminService
from backend.app.services.event_service import EventService
from backend.app.services.auth_service import require_roles

router = APIRouter(prefix="/admin", tags=["Administration"])


@router.get("/users", response_model=List[UserOut])
def get_all_users(
    db: Session = Depends(get_db),
    admin: User = Depends(require_roles([UserRole.ADMIN]))
):
    """Admin-only: Retrieve all registered users across all roles."""
    return AdminService.list_users(db)


@router.put("/users/{user_id}/role", response_model=UserOut)
def update_user_role(
    user_id: int,
    payload: UserRoleUpdate,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(require_roles([UserRole.ADMIN]))
):
    """Admin-only: Update a user's assigned role."""
    client_ip = request.client.host if request.client else None
    return AdminService.update_user_role(
        db=db,
        user_id=user_id,
        new_role=payload.role,
        admin_user=admin,
        client_ip=client_ip
    )


@router.get("/events", response_model=List[EventOut])
def get_all_events(
    db: Session = Depends(get_db),
    admin: User = Depends(require_roles([UserRole.ADMIN]))
):
    """Admin-only: System-wide event oversight."""
    return EventService.list_events(db)


@router.get("/stats", response_model=SystemStatsOut)
def get_system_statistics(
    db: Session = Depends(get_db),
    admin: User = Depends(require_roles([UserRole.ADMIN]))
):
    """Admin-only: High-level operational and capacity statistics."""
    return AdminService.get_system_stats(db)


@router.get("/audit-logs", response_model=List[AuditLogOut])
def get_audit_logs(
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    admin: User = Depends(require_roles([UserRole.ADMIN]))
):
    """Admin-only: Inspect security audit log entries for non-repudiation."""
    return AdminService.list_audit_logs(db, limit=limit)
