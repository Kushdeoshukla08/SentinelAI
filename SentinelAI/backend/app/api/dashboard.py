from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.core.database import get_db

from app.models.log import Log
from app.models.alert import Alert


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get("/stats")
def get_dashboard_stats(
    db: Session = Depends(get_db)
):

    total_logs = db.query(Log).count()

    total_alerts = db.query(Alert).count()

    high_risk_events = (
        db.query(Log)
        .filter(Log.risk_score >= 80)
        .count()
    )

    critical_alerts = (
        db.query(Alert)
        .filter(Alert.severity == "critical")
        .count()
    )

    return {
        "total_logs": total_logs,
        "total_alerts": total_alerts,
        "high_risk_events": high_risk_events,
        "critical_alerts": critical_alerts
    }