from datetime import datetime

from pydantic import BaseModel


class AssetCreate(BaseModel):
    name: str
    asset_type: str
    owner: str | None = None
    criticality: str = "medium"
    environment: str = "production"
    ip_address: str | None = None


class AssetUpdate(BaseModel):
    name: str | None = None
    asset_type: str | None = None
    owner: str | None = None
    criticality: str | None = None
    environment: str | None = None
    ip_address: str | None = None
    status: str | None = None


class AssetResponse(BaseModel):
    id: int
    name: str
    asset_type: str
    owner: str | None
    criticality: str
    environment: str
    ip_address: str | None
    status: str
    risk_score: int
    created_at: datetime

    class Config:
        from_attributes = True
