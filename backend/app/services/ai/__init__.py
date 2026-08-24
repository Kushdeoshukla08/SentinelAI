from app.core.config import settings

from app.services.ai.local_provider import LocalProvider
from app.services.ai.openai_provider import OpenAIProvider


def get_ai_provider():
    if settings.OPENAI_API_KEY:
        return OpenAIProvider()
    return LocalProvider()
