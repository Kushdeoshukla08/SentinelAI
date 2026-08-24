from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.dependencies import require_role

from app.models.asset import Asset

from app.schemas.asset import (
    AssetCreate,
    AssetUpdate,
    AssetResponse
)

from app.services.asset_risk import calculate_asset_risk
from app.services.audit_service import log_audit

router = APIRouter(
    prefix="/assets",
    tags=["Assets"]
)

CAN_MODIFY = require_role("admin", "security_manager", "analyst")

VALID_CRITICALITY = {"low", "medium", "high", "critical"}
VALID_STATUS = {"active", "inactive", "decommissioned"}


def with_risk_score(db: Session, asset: Asset) -> Asset:
    asset.risk_score = calculate_asset_risk(db, asset.ip_address)
    return asset


def get_asset_or_404(db: Session, asset_id: int) -> Asset:

    asset = (
        db.query(Asset)
        .filter(Asset.id == asset_id)
        .first()
    )

    if not asset:
        raise HTTPException(
            status_code=404,
            detail="Asset not found"
        )

    return asset


@router.post(
    "/",
    response_model=AssetResponse
)
def create_asset(
    asset: AssetCreate,
    db: Session = Depends(get_db),
    current_user=Depends(CAN_MODIFY)
):

    if asset.criticality not in VALID_CRITICALITY:
        raise HTTPException(
            status_code=400,
            detail=f"criticality must be one of {sorted(VALID_CRITICALITY)}"
        )

    new_asset = Asset(
        name=asset.name,
        asset_type=asset.asset_type,
        owner=asset.owner,
        criticality=asset.criticality,
        environment=asset.environment,
        ip_address=asset.ip_address
    )

    db.add(new_asset)
    db.commit()
    db.refresh(new_asset)

    log_audit(
        db,
        actor_email=current_user.get("sub"),
        action="ASSET_CREATED",
        resource_type="asset",
        resource_id=new_asset.id,
        details=f"name={new_asset.name}"
    )

    return with_risk_score(db, new_asset)


@router.get(
    "/",
    response_model=list[AssetResponse]
)
def list_assets(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    assets = db.query(Asset).all()

    return [with_risk_score(db, asset) for asset in assets]


@router.get(
    "/{asset_id}",
    response_model=AssetResponse
)
def get_asset(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    asset = get_asset_or_404(db, asset_id)

    return with_risk_score(db, asset)


@router.patch(
    "/{asset_id}",
    response_model=AssetResponse
)
def update_asset(
    asset_id: int,
    asset_update: AssetUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(CAN_MODIFY)
):

    asset = get_asset_or_404(db, asset_id)

    update_data = asset_update.model_dump(exclude_unset=True)

    if "criticality" in update_data and update_data["criticality"] not in VALID_CRITICALITY:
        raise HTTPException(
            status_code=400,
            detail=f"criticality must be one of {sorted(VALID_CRITICALITY)}"
        )

    if "status" in update_data and update_data["status"] not in VALID_STATUS:
        raise HTTPException(
            status_code=400,
            detail=f"status must be one of {sorted(VALID_STATUS)}"
        )

    for field, value in update_data.items():
        setattr(asset, field, value)

    db.commit()
    db.refresh(asset)

    log_audit(
        db,
        actor_email=current_user.get("sub"),
        action="ASSET_UPDATED",
        resource_type="asset",
        resource_id=asset.id,
        details=", ".join(f"{k}={v}" for k, v in update_data.items())
    )

    return with_risk_score(db, asset)


@router.delete("/{asset_id}")
def delete_asset(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin"))
):

    asset = get_asset_or_404(db, asset_id)

    db.delete(asset)
    db.commit()

    log_audit(
        db,
        actor_email=current_user.get("sub"),
        action="ASSET_DELETED",
        resource_type="asset",
        resource_id=asset_id
    )

    return {"detail": "Asset deleted"}
