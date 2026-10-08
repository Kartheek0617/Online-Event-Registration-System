import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Enum as SQLEnum, Index, text
from sqlalchemy.orm import relationship
from backend.app.db.base import Base


class RegistrationStatus(str, enum.Enum):
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"


class Registration(Base):
    __tablename__ = "registrations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    registered_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    status = Column(SQLEnum(RegistrationStatus), default=RegistrationStatus.CONFIRMED, nullable=False, index=True)
    cancelled_at = Column(DateTime, nullable=True)

    __table_args__ = (
        # Partial unique index ensuring a student can have at most one CONFIRMED registration per event
        Index(
            "uq_event_student_active",
            "event_id",
            "student_id",
            unique=True,
            postgresql_where=text("status = 'CONFIRMED'"),
            sqlite_where=text("status = 'CONFIRMED'")
        ),
    )

    # Relationships
    event = relationship("Event", back_populates="registrations")
    student = relationship("User", back_populates="registrations")

    def __repr__(self):
        return f"<Registration id={self.id} event_id={self.event_id} student_id={self.student_id} status={self.status}>"
