from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.dependencies import require_role

from app.models.alert import Alert

from app.schemas.alert import (
    AlertResponse,
    AlertUpdate,
    AlertAssign,
    AlertResolve
)

from app.services.audit_service import log_audit

router = APIRouter(
    prefix="/alerts",
    tags=["Alerts"]
)

CAN_MODIFY = require_role("admin", "security_manager", "analyst")

VALID_STATUSES = {"new", "acknowledged", "investigating", "resolved"}


def get_alert_or_404(db: Session, alert_id: int) -> Alert:

    alert = (
        db.query(Alert)
        .filter(Alert.id == alert_id)
        .first()
    )

    if not alert:
        raise HTTPException(
            status_code=404,
            detail="Alert not found"
        )

    return alert


@router.get(
    "/",
    response_model=list[AlertResponse]
)
def get_alerts(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    alerts = db.query(Alert).all()

    return alerts


@router.patch(
    "/{alert_id}",
    response_model=AlertResponse
)
def update_alert_status(
    alert_id: int,
    alert_update: AlertUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(CAN_MODIFY)
):

    if alert_update.status not in VALID_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"status must be one of {sorted(VALID_STATUSES)}"
        )

    alert = get_alert_or_404(db, alert_id)

    old_status = alert.status
    alert.status = alert_update.status

    db.commit()
    db.refresh(alert)

    log_audit(
        db,
        actor_email=current_user.get("sub"),
        action="ALERT_STATUS_CHANGED",
        resource_type="alert",
        resource_id=alert.id,
        details=f"{old_status} -> {alert.status}"
    )

    return alert


@router.patch(
    "/{alert_id}/assign",
    response_model=AlertResponse
)
def assign_alert(
    alert_id: int,
    assignment: AlertAssign,
    db: Session = Depends(get_db),
    current_user=Depends(CAN_MODIFY)
):

    alert = get_alert_or_404(db, alert_id)

    alert.assigned_to = assignment.assigned_to

    db.commit()
    db.refresh(alert)

    log_audit(
        db,
        actor_email=current_user.get("sub"),
        action="ALERT_ASSIGNED",
        resource_type="alert",
        resource_id=alert.id,
        details=f"assigned_to={alert.assigned_to}"
    )

    return alert


@router.patch(
    "/{alert_id}/resolve",
    response_model=AlertResponse
)
def resolve_alert(
    alert_id: int,
    resolution: AlertResolve,
    db: Session = Depends(get_db),
    current_user=Depends(CAN_MODIFY)
):

    alert = get_alert_or_404(db, alert_id)

    alert.status = "resolved"
    alert.resolution_notes = resolution.resolution_notes

    db.commit()
    db.refresh(alert)

    log_audit(
        db,
        actor_email=current_user.get("sub"),
        action="ALERT_RESOLVED",
        resource_type="alert",
        resource_id=alert.id
    )

    return alert
