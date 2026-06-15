from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.users import router as users_router

from app.core.database import Base
from app.core.database import engine

from app.models.user import User

app = FastAPI(
    title="SentinelAI",
    description="AI-Powered Security Operations Center",
    version="1.0.0"
)

Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(users_router)


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