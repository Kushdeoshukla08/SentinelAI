from datetime import datetime

from pydantic import BaseModel


class IOCCreate(BaseModel):
    ioc_type: str
    value: str
    source: str | None = None
    confidence: int = 50
    severity: str = "medium"
    tags: str | None = None


class IOCUpdate(BaseModel):
    confidence: int | None = None
    severity: str | None = None
    tags: str | None = None
    is_active: bool | None = None


class IOCResponse(BaseModel):
    id: int
    ioc_type: str
    value: str
    source: str | None
    confidence: int
    severity: str
    tags: str | None
    is_active: bool
    first_seen: datetime
    last_seen: datetime

    class Config:
        from_attributes = True
