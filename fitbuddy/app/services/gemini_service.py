from __future__ import annotations

from functools import lru_cache

from google import genai

from ..config import get_settings


class GeminiService:
    """Small wrapper around Google's current Gen AI Python SDK."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = genai.Client(api_key=self.settings.gemini_api_key) if self.settings.ai_enabled else None

    def generate(self, *, model: str, prompt: str) -> str:
        if not self.client:
            raise RuntimeError("Gemini API key is not configured")
        response = self.client.models.generate_content(model=model, contents=prompt)
        text = getattr(response, "text", None)
        if not text:
            raise RuntimeError("Gemini returned an empty response")
        return text.strip()


@lru_cache
def get_gemini_service() -> GeminiService:
    return GeminiService()
