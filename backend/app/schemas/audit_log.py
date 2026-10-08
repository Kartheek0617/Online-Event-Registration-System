from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AuditLogOut(BaseModel):
    id: int
    actor_id: Optional[int]
    actor_name: Optional[str] = None
    actor_email: Optional[str] = None
    action: str
    entity_type: str
    entity_id: Optional[int]
    timestamp: datetime
    source_ip: Optional[str]
    result: str
    metadata_json: Optional[str]

    class Config:
        from_attributes = True


class SystemStatsOut(BaseModel):
    total_users: int
    total_students: int
    total_faculty: int
    total_events: int
    active_events: int
    total_registrations: int
    confirmed_registrations: int
    total_audit_logs: int
