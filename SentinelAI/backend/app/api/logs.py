from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.core.database import get_db

from app.models.log import Log

from app.schemas.log import LogCreate

from app.services.risk_engine import calculate_risk


router = APIRouter(
    prefix="/logs",
    tags=["Logs"]
)


@router.post("/upload")
def upload_log(
    log: LogCreate,
    db: Session = Depends(get_db)
):

    risk_score, severity = calculate_risk(
        log.event_type
    )

    new_log = Log(
        source_ip=log.source_ip,
        event_type=log.event_type,
        username=log.username,
        risk_score=risk_score,
        severity=severity
    )

    db.add(new_log)
    db.commit()
    db.refresh(new_log)

    return {
        "id": new_log.id,
        "source_ip": new_log.source_ip,
        "event_type": new_log.event_type,
        "username": new_log.username,
        "risk_score": new_log.risk_score,
        "severity": new_log.severity
    }


@router.get("/")
def get_logs(
    db: Session = Depends(get_db)
):

    logs = db.query(Log).all()

    return logs