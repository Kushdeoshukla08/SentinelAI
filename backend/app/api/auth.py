from uuid import uuid4

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.core.database import get_db

from app.core.security import hash_password
from app.core.security import verify_password
from app.core.security import create_access_token

from app.models.user import User

from app.schemas.user import UserCreate
from app.schemas.user import UserLogin
from app.schemas.user import UserResponse
from app.schemas.user import Token

from app.services.audit_service import log_audit

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=UserResponse
)
def register_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):

    existing_user = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    is_first_user = db.query(User).count() == 0

    new_user = User(
        id=str(uuid4()),
        name=user.name,
        email=user.email,
        password_hash=hash_password(user.password),
        role="admin" if is_first_user else "analyst"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    log_audit(
        db,
        actor_email=new_user.email,
        action="USER_REGISTERED",
        resource_type="user",
        resource_id=new_user.id,
        details=f"role={new_user.role}"
    )

    return new_user


@router.post(
    "/login",
    response_model=Token
)
def login_user(
    user: UserLogin,
    db: Session = Depends(get_db)
):

    existing_user = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    if not existing_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    if not verify_password(
        user.password,
        existing_user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    token = create_access_token(
        {
            "sub": existing_user.email,
            "role": existing_user.role
        }
    )

    log_audit(
        db,
        actor_email=existing_user.email,
        action="USER_LOGIN",
        resource_type="user",
        resource_id=existing_user.id
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@router.get("/test")
def auth_test():
    return {
        "message": "Authentication API Working"
    }