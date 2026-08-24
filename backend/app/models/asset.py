from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy.sql import func

from app.core.database import Base


class Asset(Base):
    __tablename__ = "assets"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String,
        nullable=False
    )

    asset_type = Column(
        String,
        nullable=False
    )

    owner = Column(
        String,
        nullable=True
    )

    criticality = Column(
        String,
        nullable=False,
        server_default="medium"
    )

    environment = Column(
        String,
        nullable=False,
        server_default="production"
    )

    ip_address = Column(
        String,
        nullable=True
    )

    status = Column(
        String,
        nullable=False,
        server_default="active"
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
