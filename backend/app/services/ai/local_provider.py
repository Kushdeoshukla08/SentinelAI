from sqlalchemy.orm import Session

from app.models.alert import Alert
from app.models.incident import Incident
from app.models.log import Log
from app.models.ioc import IOC

from app.services.ai.base import AIProvider

# Incidents have no FK to the alert that spawned them (a known schema gap,
# documented in docs/Architecture.md). Both alert-generating pipelines use a
# fixed, predictable incident title, so that's what we correlate on here.
INCIDENT_TO_ALERT_TYPE = {
    "Brute Force Attack Detected": "Brute Force Attack",
    "Known Malicious IP Detected": "Known Malicious IP"
}


class LocalProvider(AIProvider):
    name = "local"

    def explain_alert(self, db: Session, alert: Alert) -> dict:

        if alert.alert_type == "Brute Force Attack":
            return self._explain_brute_force(db, alert)

        if alert.alert_type == "Known Malicious IP":
            return self._explain_known_malicious_ip(db, alert)

        return self._explain_generic_alert(db, alert)

    def _explain_brute_force(self, db: Session, alert: Alert) -> dict:

        related_logs = (
            db.query(Log)
            .filter(
                Log.source_ip == alert.source_ip,
                Log.event_type == "failed_login"
            )
            .order_by(Log.created_at.asc())
            .all()
        )

        evidence = [
            f"Log #{log.id}: failed_login from {log.source_ip} by user "
            f"'{log.username}' at {log.created_at}"
            for log in related_logs[:10]
        ]

        return {
            "summary": (
                f"{len(related_logs)} failed login attempts were detected from "
                f"source IP {alert.source_ip}, exceeding the brute-force threshold."
            ),
            "evidence": evidence,
            "confidence": 90,
            "severity": alert.severity,
            "recommended_action": (
                "Block the source IP at the firewall/WAF, force a password reset "
                "for any targeted accounts, and enable multi-factor authentication "
                "if not already required."
            ),
            "provider": self.name
        }

    def _explain_known_malicious_ip(self, db: Session, alert: Alert) -> dict:

        ioc = (
            db.query(IOC)
            .filter(
                IOC.ioc_type == "ip",
                IOC.value == alert.source_ip
            )
            .first()
        )

        evidence = []

        if ioc:
            evidence.append(
                f"IOC #{ioc.id}: {ioc.value} flagged by source "
                f"'{ioc.source or 'unknown'}' with confidence {ioc.confidence}/100, "
                f"tags: {ioc.tags or 'none'}"
            )

        related_logs = (
            db.query(Log)
            .filter(Log.source_ip == alert.source_ip)
            .order_by(Log.created_at.desc())
            .limit(5)
            .all()
        )

        evidence.extend(
            f"Log #{log.id}: {log.event_type} from {log.source_ip} by "
            f"'{log.username}' at {log.created_at}"
            for log in related_logs
        )

        return {
            "summary": (
                f"Traffic was observed from {alert.source_ip}, which matches a "
                f"known malicious IP indicator in the threat intelligence database."
            ),
            "evidence": evidence,
            "confidence": ioc.confidence if ioc else 60,
            "severity": alert.severity,
            "recommended_action": (
                "Block the IP at the network perimeter, review any successful "
                "authentications from this IP for signs of compromise, and check "
                "for lateral movement from affected accounts."
            ),
            "provider": self.name
        }

    def _explain_generic_alert(self, db: Session, alert: Alert) -> dict:

        related_logs = (
            db.query(Log)
            .filter(Log.source_ip == alert.source_ip)
            .order_by(Log.created_at.desc())
            .limit(5)
            .all()
        )

        return {
            "summary": (
                f"Alert '{alert.alert_type}' was triggered for source IP "
                f"{alert.source_ip}: {alert.description}"
            ),
            "evidence": [
                f"Log #{log.id}: {log.event_type} from {log.source_ip} at "
                f"{log.created_at}"
                for log in related_logs
            ],
            "confidence": 50,
            "severity": alert.severity,
            "recommended_action": (
                "Investigate the source IP and affected accounts, and escalate "
                "if the activity is confirmed malicious."
            ),
            "provider": self.name
        }

    def explain_incident(self, db: Session, incident: Incident) -> dict:

        related_alert_type = INCIDENT_TO_ALERT_TYPE.get(incident.title)

        related_alerts = []

        if related_alert_type:
            related_alerts = (
                db.query(Alert)
                .filter(Alert.alert_type == related_alert_type)
                .all()
            )

        evidence = [
            f"Alert #{a.id}: {a.alert_type} from {a.source_ip}, status={a.status}"
            for a in related_alerts
        ]

        assignment_note = (
            f", assigned to {incident.assigned_to}"
            if incident.assigned_to else ", unassigned"
        )

        return {
            "summary": (
                f"Incident '{incident.title}' is currently {incident.status} "
                f"with {incident.severity} severity{assignment_note}. "
                f"{len(related_alerts)} related alert(s) found."
            ),
            "evidence": evidence,
            "confidence": 85 if related_alerts else 40,
            "severity": incident.severity,
            "recommended_action": (
                incident.resolution_notes
                if incident.status == "resolved" and incident.resolution_notes
                else "Review related alerts and evidence, assign an analyst, and "
                     "follow standard containment/eradication/recovery steps."
            ),
            "provider": self.name
        }
