from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.core.database import get_db

from app.models.incident import Incident

from app.schemas.incident import (
    IncidentCreate,
    IncidentResponse
)


router = APIRouter(
    prefix="/incidents",
    tags=["Incidents"]
)


@router.post(
    "/",
    response_model=IncidentResponse
)
def create_incident(
    incident: IncidentCreate,
    db: Session = Depends(get_db)
):

    new_incident = Incident(
        title=incident.title,
        severity=incident.severity
    )

    db.add(new_incident)
    db.commit()
    db.refresh(new_incident)

    return new_incident


@router.get("/")
def get_incidents(
    db: Session = Depends(get_db)
):

    incidents = db.query(
        Incident
    ).all()

    return incidents