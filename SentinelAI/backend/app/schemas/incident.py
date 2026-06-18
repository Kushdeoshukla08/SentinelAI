from pydantic import BaseModel


class IncidentCreate(BaseModel):
    title: str
    severity: str


class IncidentResponse(BaseModel):
    id: int
    title: str
    severity: str
    status: str

    class Config:
        from_attributes = True