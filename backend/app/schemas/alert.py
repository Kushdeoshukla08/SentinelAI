from pydantic import BaseModel


class AlertResponse(BaseModel):
    id: int
    source_ip: str
    alert_type: str
    severity: str
    description: str

    class Config:
        from_attributes = True