from typing import List, Optional
from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.models.user import User, UserRole
from backend.app.models.event import EventStatus
from backend.app.schemas.event import EventCreate, EventUpdate, EventOut, EventDetailOut
from backend.app.services.event_service import EventService
from backend.app.services.auth_service import require_roles, get_optional_current_user

router = APIRouter(prefix="/events", tags=["Events"])


@router.get("", response_model=List[EventOut])
def list_events(
    search: Optional[str] = Query(None, description="Search term for title, description, venue"),
    category: Optional[str] = Query(None, description="Filter by event category"),
    status: Optional[EventStatus] = Query(None, description="Filter by status (OPEN, CLOSED, CANCELLED)"),
    db: Session = Depends(get_db)
):
    """
    Public endpoint: List all events with capacity metrics and search/filtering.
    Accessible to GUEST, STUDENT, FACULTY, and ADMIN.
    """
    return EventService.list_events(db, search=search, category=category, status_filter=status)


@router.get("/{event_id}", response_model=EventDetailOut)
def get_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Public endpoint: Get detailed event specifications.
    Shows current user's registration status if authenticated as a student.
    """
    return EventService.get_event_detail(db, event_id, current_user=current_user)


@router.post("", response_model=EventOut, status_code=201)
def create_event(
    payload: EventCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.FACULTY, UserRole.ADMIN]))
):
    """
    Organizer endpoint: Create a new event.
    Restricted to FACULTY and ADMIN roles only.
    """
    client_ip = request.client.host if request.client else None
    new_event = EventService.create_event(db, payload, current_user, client_ip=client_ip)
    return EventService.get_event_detail(db, new_event.id)


@router.put("/{event_id}", response_model=EventOut)
def update_event(
    event_id: int,
    payload: EventUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.FACULTY, UserRole.ADMIN]))
):
    """
    Organizer endpoint: Modify event details.
    Enforces object-level authorization: Faculty can only update their own events.
    """
    client_ip = request.client.host if request.client else None
    updated_event = EventService.update_event(db, event_id, payload, current_user, client_ip=client_ip)
    return EventService.get_event_detail(db, updated_event.id)


@router.post("/{event_id}/close", response_model=EventOut)
def close_event_registration(
    event_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.FACULTY, UserRole.ADMIN]))
):
    """
    Organizer endpoint: Close registration for an event.
    Enforces object-level authorization: Faculty can only close their own events.
    """
    client_ip = request.client.host if request.client else None
    closed_event = EventService.close_event(db, event_id, current_user, client_ip=client_ip)
    return EventService.get_event_detail(db, closed_event.id)
