import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum, CheckConstraint
from sqlalchemy.orm import relationship
from backend.app.db.base import Base


class EventStatus(str, enum.Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    organizer_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=False)
    category = Column(String(100), nullable=False, index=True)
    venue = Column(String(200), nullable=False)
    event_date = Column(String(20), nullable=False)  # ISO Date YYYY-MM-DD
    start_time = Column(String(10), nullable=False)  # HH:MM
    end_time = Column(String(10), nullable=False)    # HH:MM
    participant_limit = Column(Integer, nullable=False)
    registration_deadline = Column(String(30), nullable=False)  # ISO datetime string
    status = Column(SQLEnum(EventStatus), default=EventStatus.OPEN, nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    __table_args__ = (
        CheckConstraint("participant_limit > 0", name="chk_participant_limit_positive"),
    )

    # Relationships
    organizer = relationship("User", back_populates="organized_events")
    registrations = relationship("Registration", back_populates="event", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Event id={self.id} title={self.title} status={self.status} limit={self.participant_limit}>"
