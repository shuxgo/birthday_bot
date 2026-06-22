from openai import AsyncOpenAI

from app.config import Settings


class TextGenerationService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

    async def generate(self, prompt: str) -> str:
        if not self.client:
            return "Поздравляем с днем рождения! Желаем здоровья, энергии, новых достижений и теплых моментов каждый день."
        response = await self.client.responses.create(
            model=self.settings.openai_text_model,
            input=prompt,
        )
        return response.output_text.strip()

