from fastapi import APIRouter
from fastapi import Depends

from app.core.dependencies import get_current_user

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get("/me")
def get_current_user_details(
    current_user=Depends(get_current_user)
):

    return {
        "message": "Protected Route Working",
        "user": current_user
    }