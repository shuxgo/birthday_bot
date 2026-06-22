import logging

import httpx
from openai import AsyncOpenAI
from openai import OpenAIError

from app.config import Settings

logger = logging.getLogger(__name__)


class TextGenerationService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.openai_client = (
            AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
        )

    async def generate(self, prompt: str) -> str:
        if self.settings.ai_provider.lower() == "gemini":
            return await self._generate_gemini(prompt)
        if self.settings.ai_provider.lower() == "openai":
            return await self._generate_openai(prompt)
        logger.warning("Unknown AI_PROVIDER=%s, using fallback text", self.settings.ai_provider)
        return fallback_birthday_text()

    async def _generate_gemini(self, prompt: str) -> str:
        if not self.settings.gemini_api_key:
            return fallback_birthday_text()
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.settings.gemini_text_model}:generateContent"
        )
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}],
                }
            ],
            "generationConfig": {
                "temperature": 0.8,
                "maxOutputTokens": 700,
            },
        }
        try:
            async with httpx.AsyncClient(timeout=40) as client:
                response = await client.post(
                    url,
                    params={"key": self.settings.gemini_api_key},
                    json=payload,
                )
                response.raise_for_status()
            data = response.json()
            parts = data["candidates"][0]["content"]["parts"]
            text = "".join(part.get("text", "") for part in parts).strip()
            return text or fallback_birthday_text()
        except Exception as exc:
            logger.warning("Gemini generation failed: %s", exc)
            return fallback_birthday_text()

    async def _generate_openai(self, prompt: str) -> str:
        if not self.openai_client:
            return fallback_birthday_text()
        try:
            response = await self.openai_client.responses.create(
                model=self.settings.openai_text_model,
                input=prompt,
            )
            return response.output_text.strip()
        except OpenAIError as exc:
            logger.warning("OpenAI generation failed: %s", exc)
            return fallback_birthday_text()


def fallback_birthday_text() -> str:
    return (
        "Поздравляем с днем рождения! Желаем крепкого здоровья, энергии, "
        "новых профессиональных достижений, благополучия и тёплых моментов каждый день."
    )
