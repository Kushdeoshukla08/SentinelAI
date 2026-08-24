from datetime import datetime

from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    id: int
    actor_email: str
    action: str
    resource_type: str | None
    resource_id: str | None
    details: str | None
    created_at: datetime

    class Config:
        from_attributes = True
