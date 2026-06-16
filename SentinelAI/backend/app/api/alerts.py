from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.core.database import get_db

from app.models.alert import Alert


router = APIRouter(
    prefix="/alerts",
    tags=["Alerts"]
)


@router.get("/")
def get_alerts(
    db: Session = Depends(get_db)
):

    alerts = db.query(Alert).all()

    return alerts