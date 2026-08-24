from pydantic import BaseModel


class AlertResponse(BaseModel):
    id: int
    source_ip: str
    alert_type: str
    severity: str
    description: str
    status: str
    assigned_to: str | None

    class Config:
        from_attributes = True


class AlertUpdate(BaseModel):
    status: str


class AlertAssign(BaseModel):
    assigned_to: str


class AlertResolve(BaseModel):
    resolution_notes: str
