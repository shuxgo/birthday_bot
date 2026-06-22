import pytest

from app.config import Settings
from app.services.text_generation import TextGenerationService


@pytest.mark.asyncio
async def test_gemini_without_key_uses_fallback():
    settings = Settings(
        BOT_TOKEN="token",
        DATABASE_URL="postgresql+asyncpg://u:p@localhost/db",
        REDIS_URL="redis://localhost:6379/0",
        AI_PROVIDER="gemini",
        GEMINI_API_KEY="",
        INITIAL_ADMIN_IDS="1",
    )
    text = await TextGenerationService(settings).generate("test")
    assert "Поздравляем" in text
