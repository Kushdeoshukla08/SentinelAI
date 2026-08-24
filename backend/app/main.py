from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.logs import router as logs_router
from app.api.alerts import router as alerts_router
from app.api.dashboard import router as dashboard_router
from app.api.incidents import router as incidents_router
from app.api.mitre import router as mitre_router
from app.api.audit import router as audit_router

from app.core.database import Base
from app.core.database import engine

from app.models.user import User
from app.models.log import Log
from app.models.alert import Alert
from app.models.incident import Incident
from app.models.audit_log import AuditLog


app = FastAPI(
    title="SentinelAI",
    description="AI-Powered Security Operations Center",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(logs_router)
app.include_router(alerts_router)
app.include_router(dashboard_router)
app.include_router(incidents_router)
app.include_router(mitre_router)
app.include_router(audit_router)


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