from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from backend.app.models.registration import RegistrationStatus


class RegistrationOut(BaseModel):
    id: int
    event_id: int
    student_id: int
    registered_at: datetime
    status: RegistrationStatus
    cancelled_at: Optional[datetime] = None
    event_title: Optional[str] = None
    event_date: Optional[str] = None
    venue: Optional[str] = None
    category: Optional[str] = None

    class Config:
        from_attributes = True


class ParticipantOut(BaseModel):
    registration_id: int
    student_id: int
    student_name: str
    student_email: str
    registered_at: datetime
    status: RegistrationStatus

    class Config:
        from_attributes = True


class RegistrationResponse(BaseModel):
    message: str
    registration: RegistrationOut
