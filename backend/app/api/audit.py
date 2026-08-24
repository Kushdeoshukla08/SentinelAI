from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_role

from app.models.audit_log import AuditLog

from app.schemas.audit import AuditLogResponse

router = APIRouter(
    prefix="/audit",
    tags=["Audit"]
)


@router.get(
    "/",
    response_model=list[AuditLogResponse]
)
def get_audit_logs(
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin"))
):

    return (
        db.query(AuditLog)
        .order_by(AuditLog.created_at.desc())
        .all()
    )
