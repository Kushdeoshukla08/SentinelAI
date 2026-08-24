from pydantic import BaseModel


class IncidentCreate(BaseModel):
    title: str
    severity: str


class IncidentUpdate(BaseModel):
    status: str


class IncidentAssign(BaseModel):
    assigned_to: str


class IncidentResolve(BaseModel):
    resolution_notes: str


class IncidentResponse(BaseModel):
    id: int
    title: str
    severity: str
    status: str

    class Config:
        from_attributes = True