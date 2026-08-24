from pydantic import BaseModel


class AIExplanation(BaseModel):
    summary: str
    evidence: list[str]
    confidence: int
    severity: str
    recommended_action: str
    provider: str
