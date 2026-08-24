from datetime import datetime
from datetime import timezone

from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user

from app.models.log import Log
from app.models.alert import Alert
from app.models.incident import Incident

from app.schemas.log import LogCreate

from app.services.risk_engine import calculate_risk
from app.services.risk_engine import should_generate_alert

from app.services.mitre_mapper import map_event_to_mitre
from app.services.ioc_matcher import match_ip_indicator


router = APIRouter(
    prefix="/logs",
    tags=["Logs"]
)


@router.post("/upload")
def upload_log(
    log: LogCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    risk_score, severity = calculate_risk(
        log.event_type
    )

    mitre_data = map_event_to_mitre(
        log.event_type
    )

    matched_ioc = match_ip_indicator(db, log.source_ip)

    if matched_ioc:
        risk_score = 100
        severity = "critical"
        matched_ioc.last_seen = datetime.now(timezone.utc)

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

    alert_generated = False
    failed_login_count = 0

    if matched_ioc:

        existing_ioc_alert = (
            db.query(Alert)
            .filter(
                Alert.source_ip == log.source_ip,
                Alert.alert_type == "Known Malicious IP"
            )
            .first()
        )

        if not existing_ioc_alert:

            ioc_alert = Alert(
                source_ip=log.source_ip,
                alert_type="Known Malicious IP",
                severity="critical",
                description=f"Traffic from known malicious IP (IOC #{matched_ioc.id}, source={matched_ioc.source or 'unknown'})"
            )

            db.add(ioc_alert)
            db.commit()

            ioc_incident = Incident(
                title="Known Malicious IP Detected",
                severity="critical"
            )

            db.add(ioc_incident)
            db.commit()

            alert_generated = True

    if log.event_type == "failed_login":

        failed_login_count = (
            db.query(Log)
            .filter(
                Log.source_ip == log.source_ip,
                Log.event_type == "failed_login"
            )
            .count()
        )

        if should_generate_alert(
            failed_login_count
        ):

            existing_alert = (
                db.query(Alert)
                .filter(
                    Alert.source_ip == log.source_ip,
                    Alert.alert_type == "Brute Force Attack"
                )
                .first()
            )

            if not existing_alert:

                new_alert = Alert(
                    source_ip=log.source_ip,
                    alert_type="Brute Force Attack",
                    severity="critical",
                    description=f"{failed_login_count} failed login attempts detected"
                )

                db.add(new_alert)
                db.commit()

                new_incident = Incident(
                    title="Brute Force Attack Detected",
                    severity="critical"
                )

                db.add(new_incident)
                db.commit()

                alert_generated = True

    return {
        "log_id": new_log.id,
        "source_ip": new_log.source_ip,
        "event_type": new_log.event_type,
        "username": new_log.username,
        "risk_score": new_log.risk_score,
        "severity": new_log.severity,
        "mitre_technique": mitre_data["technique_id"],
        "mitre_name": mitre_data["technique_name"],
        "failed_login_count": failed_login_count,
        "alert_generated": alert_generated,
        "ioc_matched": matched_ioc is not None
    }


@router.get("/")
def get_logs(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    logs = db.query(Log).all()

    return logs     