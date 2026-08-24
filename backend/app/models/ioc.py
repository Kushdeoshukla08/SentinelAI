from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy.sql import func

from app.core.database import Base


class IOC(Base):
    __tablename__ = "iocs"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    ioc_type = Column(
        String,
        nullable=False
    )

    value = Column(
        String,
        nullable=False,
        index=True
    )

    source = Column(
        String,
        nullable=True
    )

    confidence = Column(
        Integer,
        nullable=False,
        server_default="50"
    )

    severity = Column(
        String,
        nullable=False,
        server_default="medium"
    )

    tags = Column(
        String,
        nullable=True
    )

    is_active = Column(
        Boolean,
        nullable=False,
        server_default="true"
    )

    first_seen = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    last_seen = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
