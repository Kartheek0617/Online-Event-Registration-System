from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from backend.app.models.event import EventStatus


class EventBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=5, max_length=4000)
    category: str = Field(..., min_length=2, max_length=100)
    venue: str = Field(..., min_length=2, max_length=200)
    event_date: str = Field(..., min_length=10, max_length=20, description="Format: YYYY-MM-DD")
    start_time: str = Field(..., min_length=4, max_length=10, description="Format: HH:MM")
    end_time: str = Field(..., min_length=4, max_length=10, description="Format: HH:MM")
    participant_limit: int = Field(..., gt=0, le=10000, description="Must be greater than 0")
    registration_deadline: str = Field(..., min_length=10, max_length=30, description="Format: YYYY-MM-DD or ISO")

    @field_validator("title", "category", "venue")
    def strip_and_sanitize(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Field cannot be whitespace only")
        return cleaned


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = Field(None, min_length=5, max_length=4000)
    category: Optional[str] = Field(None, min_length=2, max_length=100)
    venue: Optional[str] = Field(None, min_length=2, max_length=200)
    event_date: Optional[str] = Field(None, min_length=10, max_length=20)
    start_time: Optional[str] = Field(None, min_length=4, max_length=10)
    end_time: Optional[str] = Field(None, min_length=4, max_length=10)
    participant_limit: Optional[int] = Field(None, gt=0, le=10000)
    registration_deadline: Optional[str] = Field(None, min_length=10, max_length=30)
    status: Optional[EventStatus] = None


class EventOut(BaseModel):
    id: int
    organizer_id: int
    title: str
    description: str
    category: str
    venue: str
    event_date: str
    start_time: str
    end_time: str
    participant_limit: int
    registration_deadline: str
    status: EventStatus
    registered_count: int = 0
    available_seats: int = 0
    organizer_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EventDetailOut(EventOut):
    is_registered_by_user: bool = False
    user_registration_id: Optional[int] = None
