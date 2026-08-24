from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def log_audit(
    db: Session,
    actor_email: str,
    action: str,
    resource_type: str = None,
    resource_id: str = None,
    details: str = None
):

    entry = AuditLog(
        actor_email=actor_email,
        action=action,
        resource_type=resource_type,
        resource_id=str(resource_id) if resource_id is not None else None,
        details=details
    )

    db.add(entry)
    db.commit()
