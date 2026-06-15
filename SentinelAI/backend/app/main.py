from fastapi import FastAPI

from app.api.auth import router as auth_router

from app.core.database import Base
from app.core.database import engine

from app.models.user import User

app = FastAPI(
    title="SentinelAI",
    description="AI-Powered Security Operations Center",
    version="1.0.0"
)

# Create database tables automatically
Base.metadata.create_all(bind=engine)

# Register routers
app.include_router(auth_router)


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