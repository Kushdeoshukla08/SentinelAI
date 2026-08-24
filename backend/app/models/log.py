from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime

from sqlalchemy.sql import func

from app.core.database import Base


class Log(Base):
    __tablename__ = "logs"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    source_ip = Column(
        String,
        nullable=False
    )

    event_type = Column(
        String,
        nullable=False
    )

    username = Column(
        String,
        nullable=False
    )

    risk_score = Column(
        Integer
    )

    severity = Column(
        String
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )