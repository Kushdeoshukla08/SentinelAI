import json

from sqlalchemy.orm import Session

from openai import OpenAI

from app.core.config import settings

from app.models.alert import Alert
from app.models.incident import Incident

from app.services.ai.base import AIProvider
from app.services.ai.local_provider import LocalProvider


SYSTEM_PROMPT = (
    "You are a security operations analyst assistant for SentinelAI. You are "
    "given a JSON object that was already computed from real, structured "
    "application data (alert/incident records, logs, threat intelligence). "
    "Rewrite the \"summary\" and \"recommended_action\" fields in clearer, more "
    "natural analyst language. Keep \"evidence\", \"confidence\", and "
    "\"severity\" exactly as given - do not invent, remove, or alter facts "
    "that are not present in the input. Respond with ONLY a JSON object with "
    "keys: summary, evidence, confidence, severity, recommended_action."
)


class OpenAIProvider(AIProvider):
    name = "openai"

    def __init__(self):
        self._client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self._fallback = LocalProvider()

    def _polish(self, local_result: dict, context_label: str) -> dict:

        try:
            response = self._client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": (
                            f"Here is the structured {context_label} data:\n\n"
                            f"{json.dumps(local_result)}"
                        )
                    }
                ],
                response_format={"type": "json_object"},
                timeout=15
            )

            parsed = json.loads(response.choices[0].message.content)

            required_keys = {
                "summary", "evidence", "confidence",
                "severity", "recommended_action"
            }

            if not required_keys.issubset(parsed.keys()):
                return local_result

            parsed["provider"] = self.name
            return parsed

        except Exception:
            return local_result

    def explain_alert(self, db: Session, alert: Alert) -> dict:
        local_result = self._fallback.explain_alert(db, alert)
        return self._polish(local_result, "alert")

    def explain_incident(self, db: Session, incident: Incident) -> dict:
        local_result = self._fallback.explain_incident(db, incident)
        return self._polish(local_result, "incident")
