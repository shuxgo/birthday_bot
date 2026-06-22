from pathlib import Path

from aiogram import Bot

from app.config import Settings


class ImageGenerationService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.storage_dir = Path("storage/generated")
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    async def generate_from_telegram_photo(self, bot: Bot, file_id: str, prompt: str) -> tuple[str | None, str]:
        # MVP fallback: Telegram file_id is reused when no image-edit provider is configured.
        # The service boundary is ready for swapping this block for OpenAI Images/Replicate/etc.
        _ = (bot, prompt)
        return None, file_id

