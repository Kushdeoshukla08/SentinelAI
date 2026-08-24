from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.dependencies import require_role

from app.models.incident import Incident

from app.schemas.incident import (
    IncidentCreate,
    IncidentUpdate,
    IncidentAssign,
    IncidentResolve,
    IncidentResponse
)

from app.services.audit_service import log_audit

router = APIRouter(
    prefix="/incidents",
    tags=["Incidents"]
)

CAN_MODIFY = require_role("admin", "security_manager", "analyst")


@router.post(
    "/",
    response_model=IncidentResponse
)
def create_incident(
    incident: IncidentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(CAN_MODIFY)
):

    new_incident = Incident(
        title=incident.title,
        severity=incident.severity
    )

    db.add(new_incident)
    db.commit()
    db.refresh(new_incident)

    log_audit(
        db,
        actor_email=current_user.get("sub"),
        action="INCIDENT_CREATED",
        resource_type="incident",
        resource_id=new_incident.id,
        details=f"severity={new_incident.severity}"
    )

    return new_incident


@router.get("/")
def get_incidents(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return db.query(
        Incident
    ).all()


@router.patch("/{incident_id}")
def update_incident_status(
    incident_id: int,
    incident_update: IncidentUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(CAN_MODIFY)
):

    incident = (
        db.query(Incident)
        .filter(
            Incident.id == incident_id
        )
        .first()
    )

    if not incident:
        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )

    old_status = incident.status
    incident.status = incident_update.status

    db.commit()
    db.refresh(incident)

    log_audit(
        db,
        actor_email=current_user.get("sub"),
        action="INCIDENT_STATUS_CHANGED",
        resource_type="incident",
        resource_id=incident.id,
        details=f"{old_status} -> {incident.status}"
    )

    return {
        "id": incident.id,
        "title": incident.title,
        "status": incident.status
    }


@router.patch("/{incident_id}/assign")
def assign_incident(
    incident_id: int,
    assignment: IncidentAssign,
    db: Session = Depends(get_db),
    current_user=Depends(CAN_MODIFY)
):

    incident = (
        db.query(Incident)
        .filter(
            Incident.id == incident_id
        )
        .first()
    )

    if not incident:
        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )

    incident.assigned_to = assignment.assigned_to

    db.commit()
    db.refresh(incident)

    log_audit(
        db,
        actor_email=current_user.get("sub"),
        action="INCIDENT_ASSIGNED",
        resource_type="incident",
        resource_id=incident.id,
        details=f"assigned_to={incident.assigned_to}"
    )

    return {
        "id": incident.id,
        "title": incident.title,
        "assigned_to": incident.assigned_to
    }


@router.patch("/{incident_id}/resolve")
def resolve_incident(
    incident_id: int,
    resolution: IncidentResolve,
    db: Session = Depends(get_db),
    current_user=Depends(CAN_MODIFY)
):

    incident = (
        db.query(Incident)
        .filter(
            Incident.id == incident_id
        )
        .first()
    )

    if not incident:
        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )

    incident.status = "resolved"
    incident.resolution_notes = resolution.resolution_notes

    db.commit()
    db.refresh(incident)

    log_audit(
        db,
        actor_email=current_user.get("sub"),
        action="INCIDENT_RESOLVED",
        resource_type="incident",
        resource_id=incident.id
    )

    return {
        "id": incident.id,
        "title": incident.title,
        "status": incident.status,
        "resolution_notes": incident.resolution_notes
    }
