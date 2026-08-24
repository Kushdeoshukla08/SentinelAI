from sqlalchemy.orm import Session

from app.models.ioc import IOC


def match_ip_indicator(db: Session, ip_address: str) -> IOC | None:

    if not ip_address:
        return None

    return (
        db.query(IOC)
        .filter(
            IOC.ioc_type == "ip",
            IOC.value == ip_address,
            IOC.is_active.is_(True)
        )
        .first()
    )
