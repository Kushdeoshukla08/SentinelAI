from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.logs import router as logs_router
from app.api.alerts import router as alerts_router
from app.api.dashboard import router as dashboard_router
from app.api.incidents import router as incidents_router

from app.core.database import Base
from app.core.database import engine

from app.models.user import User
from app.models.log import Log
from app.models.alert import Alert
from app.models.incident import Incident

app = FastAPI(
    title="SentinelAI",
    description="AI-Powered Security Operations Center",
    version="1.0.0"
)

Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(logs_router)
app.include_router(alerts_router)
app.include_router(dashboard_router)
app.include_router(incidents_router)


@app.get("/")
def root():
    return {
        "message": "Welcome to SentinelAI"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }