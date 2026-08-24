from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user

from app.models.alert import Alert
from app.models.incident import Incident

from app.schemas.ai import AIExplanation

from app.services.ai import get_ai_provider

router = APIRouter(
    prefix="/ai",
    tags=["AI Analysis"]
)


@router.get(
    "/alerts/{alert_id}/explain",
    response_model=AIExplanation
)
def explain_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

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

    provider = get_ai_provider()

    return provider.explain_alert(db, alert)


@router.get(
    "/incidents/{incident_id}/explain",
    response_model=AIExplanation
)
def explain_incident(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    incident = (
        db.query(Incident)
        .filter(Incident.id == incident_id)
        .first()
    )

    if not incident:
        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )

    provider = get_ai_provider()

    return provider.explain_incident(db, incident)
