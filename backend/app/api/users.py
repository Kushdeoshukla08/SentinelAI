from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.dependencies import require_role

from app.models.user import User

from app.schemas.user import UserResponse
from app.schemas.user import UserRoleUpdate

from app.services.audit_service import log_audit

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

VALID_ROLES = {"admin", "security_manager", "analyst", "viewer"}


@router.get("/me")
def get_current_user_details(
    current_user=Depends(get_current_user)
):

    return {
        "message": "Protected Route Working",
        "user": current_user
    }


@router.get(
    "/",
    response_model=list[UserResponse]
)
def list_users(
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin"))
):

    return db.query(User).all()


@router.patch(
    "/{user_id}/role",
    response_model=UserResponse
)
def update_user_role(
    user_id: str,
    role_update: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin"))
):

    if role_update.role not in VALID_ROLES:
        raise HTTPException(
            status_code=400,
            detail=f"role must be one of {sorted(VALID_ROLES)}"
        )

    target_user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not target_user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    old_role = target_user.role
    target_user.role = role_update.role

    db.commit()
    db.refresh(target_user)

    log_audit(
        db,
        actor_email=current_user.get("sub"),
        action="USER_ROLE_CHANGED",
        resource_type="user",
        resource_id=target_user.id,
        details=f"{old_role} -> {target_user.role}"
    )

    return target_user
