from openai import AsyncOpenAI
from openai import OpenAIError

from app.config import Settings


class TextGenerationService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

    async def generate(self, prompt: str) -> str:
        if not self.client:
            return fallback_birthday_text()
        try:
            response = await self.client.responses.create(
                model=self.settings.openai_text_model,
                input=prompt,
            )
            return response.output_text.strip()
        except OpenAIError:
            return fallback_birthday_text()


def fallback_birthday_text() -> str:
    return (
        "Поздравляем с днем рождения! Желаем крепкого здоровья, энергии, "
        "новых профессиональных достижений, благополучия и тёплых моментов каждый день."
    )
