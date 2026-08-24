from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy.sql import func

from app.core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    actor_email = Column(
        String,
        nullable=False
    )

    action = Column(
        String,
        nullable=False
    )

    resource_type = Column(
        String,
        nullable=True
    )

    resource_id = Column(
        String,
        nullable=True
    )

    details = Column(
        String,
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
