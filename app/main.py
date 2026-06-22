import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

from app.bot.middlewares.auth import AuthMiddleware
from app.bot.middlewares.db import DbSessionMiddleware
from app.bot.routers import build_router
from app.config import get_settings
from app.database.repositories.prompts import PromptRepository
from app.database.repositories.settings import SettingsRepository
from app.database.repositories.users import seed_initial_admins
from app.database.session import SessionFactory, create_schema
from app.services.scheduler import build_scheduler
from app.utils.logging import configure_logging

logger = logging.getLogger(__name__)


async def bootstrap() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)
    await create_schema()
    async with SessionFactory() as session:
        await seed_initial_admins(session, settings.admin_ids)
        await PromptRepository(session).ensure_defaults()
        if settings.channel_id:
            await SettingsRepository(session).set("channel_id", settings.channel_id)
        await session.commit()


async def main() -> None:
    settings = get_settings()
    await bootstrap()

    bot = Bot(token=settings.bot_token)
    redis = Redis.from_url(settings.redis_url)
    dp = Dispatcher(storage=RedisStorage(redis=redis))
    dp.update.middleware(DbSessionMiddleware())
    dp.message.middleware(AuthMiddleware(settings))
    dp.callback_query.middleware(AuthMiddleware(settings))
    dp.include_router(build_router())

    scheduler = build_scheduler(bot, settings)
    scheduler.start()
    logger.info("Birthday bot started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

