from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.dependencies import require_role

from app.models.ioc import IOC

from app.schemas.ioc import (
    IOCCreate,
    IOCUpdate,
    IOCResponse
)

from app.services.audit_service import log_audit

router = APIRouter(
    prefix="/iocs",
    tags=["Threat Intelligence"]
)

CAN_MODIFY = require_role("admin", "security_manager", "analyst")

VALID_TYPES = {"ip", "domain", "url", "hash", "email"}
VALID_SEVERITY = {"low", "medium", "high", "critical"}


def get_ioc_or_404(db: Session, ioc_id: int) -> IOC:

    ioc = (
        db.query(IOC)
        .filter(IOC.id == ioc_id)
        .first()
    )

    if not ioc:
        raise HTTPException(
            status_code=404,
            detail="IOC not found"
        )

    return ioc


@router.post(
    "/",
    response_model=IOCResponse
)
def create_ioc(
    ioc: IOCCreate,
    db: Session = Depends(get_db),
    current_user=Depends(CAN_MODIFY)
):

    if ioc.ioc_type not in VALID_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"ioc_type must be one of {sorted(VALID_TYPES)}"
        )

    if ioc.severity not in VALID_SEVERITY:
        raise HTTPException(
            status_code=400,
            detail=f"severity must be one of {sorted(VALID_SEVERITY)}"
        )

    if not (0 <= ioc.confidence <= 100):
        raise HTTPException(
            status_code=400,
            detail="confidence must be between 0 and 100"
        )

    existing = (
        db.query(IOC)
        .filter(
            IOC.ioc_type == ioc.ioc_type,
            IOC.value == ioc.value
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="An IOC with this type and value already exists"
        )

    new_ioc = IOC(
        ioc_type=ioc.ioc_type,
        value=ioc.value,
        source=ioc.source,
        confidence=ioc.confidence,
        severity=ioc.severity,
        tags=ioc.tags
    )

    db.add(new_ioc)
    db.commit()
    db.refresh(new_ioc)

    log_audit(
        db,
        actor_email=current_user.get("sub"),
        action="IOC_CREATED",
        resource_type="ioc",
        resource_id=new_ioc.id,
        details=f"{new_ioc.ioc_type}={new_ioc.value}"
    )

    return new_ioc


@router.get(
    "/",
    response_model=list[IOCResponse]
)
def list_iocs(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return db.query(IOC).all()


@router.get(
    "/{ioc_id}",
    response_model=IOCResponse
)
def get_ioc(
    ioc_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return get_ioc_or_404(db, ioc_id)


@router.patch(
    "/{ioc_id}",
    response_model=IOCResponse
)
def update_ioc(
    ioc_id: int,
    ioc_update: IOCUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(CAN_MODIFY)
):

    ioc = get_ioc_or_404(db, ioc_id)

    update_data = ioc_update.model_dump(exclude_unset=True)

    if "severity" in update_data and update_data["severity"] not in VALID_SEVERITY:
        raise HTTPException(
            status_code=400,
            detail=f"severity must be one of {sorted(VALID_SEVERITY)}"
        )

    if "confidence" in update_data and not (0 <= update_data["confidence"] <= 100):
        raise HTTPException(
            status_code=400,
            detail="confidence must be between 0 and 100"
        )

    for field, value in update_data.items():
        setattr(ioc, field, value)

    db.commit()
    db.refresh(ioc)

    log_audit(
        db,
        actor_email=current_user.get("sub"),
        action="IOC_UPDATED",
        resource_type="ioc",
        resource_id=ioc.id,
        details=", ".join(f"{k}={v}" for k, v in update_data.items())
    )

    return ioc


@router.delete("/{ioc_id}")
def delete_ioc(
    ioc_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin"))
):

    ioc = get_ioc_or_404(db, ioc_id)

    db.delete(ioc)
    db.commit()

    log_audit(
        db,
        actor_email=current_user.get("sub"),
        action="IOC_DELETED",
        resource_type="ioc",
        resource_id=ioc_id
    )

    return {"detail": "IOC deleted"}
