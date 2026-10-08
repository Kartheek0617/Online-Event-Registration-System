from typing import List
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.models.user import User, UserRole
from backend.app.schemas.registration import RegistrationOut, ParticipantOut, RegistrationResponse
from backend.app.services.registration_service import RegistrationService
from backend.app.services.auth_service import require_roles, get_current_user

router = APIRouter(tags=["Registrations"])


@router.post("/events/{event_id}/register", response_model=RegistrationResponse, status_code=status.HTTP_201_CREATED)
def register_for_event(
    event_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.STUDENT, UserRole.ADMIN]))
):
    """
    Student action: Register for an event.
    Atomic, concurrency-safe, duplicate-preventing endpoint.
    """
    client_ip = request.client.host if request.client else None
    reg = RegistrationService.register_student_for_event(
        db=db,
        event_id=event_id,
        student=current_user,
        client_ip=client_ip
    )
    reg_out = RegistrationOut(
        id=reg.id,
        event_id=reg.event_id,
        student_id=reg.student_id,
        registered_at=reg.registered_at,
        status=reg.status,
        cancelled_at=reg.cancelled_at,
        event_title=reg.event.title if reg.event else None,
        event_date=reg.event.event_date if reg.event else None,
        venue=reg.event.venue if reg.event else None,
        category=reg.event.category if reg.event else None
    )
    return RegistrationResponse(
        message="Registration successful!",
        registration=reg_out
    )


@router.delete("/registrations/{registration_id}")
def cancel_registration(
    registration_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.STUDENT, UserRole.ADMIN]))
):
    """
    Student action: Cancel own registration.
    Enforces object-level authorization (Student A cannot cancel Student B's registration).
    Immediately updates available seats.
    """
    client_ip = request.client.host if request.client else None
    RegistrationService.cancel_registration(
        db=db,
        registration_id=registration_id,
        current_user=current_user,
        client_ip=client_ip
    )
    return {"message": "Registration successfully cancelled."}


@router.get("/registrations/me", response_model=List[RegistrationOut])
def get_my_registrations(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.STUDENT, UserRole.ADMIN]))
):
    """
    Student view: View exclusively own event registrations.
    Guarantees privacy: No student can inspect another student's registrations.
    """
    return RegistrationService.get_student_registrations(db, student=current_user)


@router.get("/events/{event_id}/participants", response_model=List[ParticipantOut])
def get_event_participants(
    event_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.FACULTY, UserRole.ADMIN]))
):
    """
    Organizer view: View confirmed participants for own event.
    Enforces object-level authorization: Faculty A cannot inspect Faculty B's participants.
    Student and Guest roles are rejected with 403 Forbidden.
    """
    client_ip = request.client.host if request.client else None
    return RegistrationService.get_event_participants(
        db=db,
        event_id=event_id,
        current_user=current_user,
        client_ip=client_ip
    )
