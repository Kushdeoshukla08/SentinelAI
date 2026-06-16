from pydantic import BaseModel


class LogCreate(BaseModel):
    source_ip: str
    event_type: str
    username: str


class LogResponse(BaseModel):
    source_ip: str
    event_type: str
    username: str
    risk_score: int
    severity: str

    class Config:
        from_attributes = True