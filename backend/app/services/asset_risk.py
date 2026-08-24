from sqlalchemy.orm import Session

from app.models.alert import Alert

SEVERITY_WEIGHTS = {
    "critical": 40,
    "high": 25,
    "medium": 10,
    "low": 5
}


def calculate_asset_risk(db: Session, ip_address: str | None) -> int:

    if not ip_address:
        return 0

    unresolved_alerts = (
        db.query(Alert)
        .filter(
            Alert.source_ip == ip_address,
            Alert.status != "resolved"
        )
        .all()
    )

    score = sum(
        SEVERITY_WEIGHTS.get(alert.severity, 0)
        for alert in unresolved_alerts
    )

    return min(score, 100)
