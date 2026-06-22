import logging
from datetime import datetime

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import Settings
from app.database.repositories.posts import PostRepository
from app.database.repositories.settings import SettingsRepository
from app.database.session import SessionFactory
from app.services.daily_digest import send_daily_digest
from app.services.post_publication import PostPublicationService

logger = logging.getLogger(__name__)


def build_scheduler(bot: Bot, settings: Settings) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone=settings.tz)

    async def publish_due_posts() -> None:
        async with SessionFactory() as session:
            now = datetime.now(settings.tz)
            posts = await PostRepository(session).list_due(now)
            channel_id = await SettingsRepository(session).get("channel_id", settings.channel_id)
            for post in posts:
                try:
                    await PostPublicationService(bot, session, channel_id).publish(post)
                except Exception as exc:
                    logger.exception("Publication failed for post %s", post.id)
                    post.status = "failed"
                    post.last_error = str(exc)
            await session.commit()

    async def daily_digest() -> None:
        async with SessionFactory() as session:
            await send_daily_digest(bot, session, datetime.now(settings.tz))
            await session.commit()

    scheduler.add_job(publish_due_posts, "interval", minutes=1, id="publish_due_posts")
    scheduler.add_job(daily_digest, "cron", hour=10, minute=0, id="daily_digest")
    return scheduler
