from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings
from app.database.models import UserRole
from app.database.repositories.users import UserRepository


class AuthMiddleware(BaseMiddleware):
    def __init__(self, settings: Settings):
        self.settings = settings

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        session: AsyncSession = data["session"]
        event_user = data.get("event_from_user")
        if not event_user:
            return await handler(event, data)

        repo = UserRepository(session)
        user = await repo.get_by_telegram_id(event_user.id)
        if not user and event_user.id in self.settings.admin_ids:
            user = await repo.upsert_user(
                event_user.id, UserRole.ADMIN, event_user.username, event_user.full_name
            )
            await session.commit()

        if not user or not user.is_active:
            if hasattr(event, "answer"):
                await event.answer("У вас нет доступа к этому боту")
            return None

        data["db_user"] = user
        return await handler(event, data)

