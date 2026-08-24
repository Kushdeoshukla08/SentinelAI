from abc import ABC
from abc import abstractmethod

from sqlalchemy.orm import Session

from app.models.alert import Alert
from app.models.incident import Incident


class AIProvider(ABC):
    name: str

    @abstractmethod
    def explain_alert(self, db: Session, alert: Alert) -> dict:
        ...

    @abstractmethod
    def explain_incident(self, db: Session, incident: Incident) -> dict:
        ...
