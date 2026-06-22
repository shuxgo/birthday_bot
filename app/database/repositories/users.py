from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User, UserRole


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        result = await self.session.execute(select(User).where(User.telegram_id == telegram_id))
        return result.scalar_one_or_none()

    async def list_moderators(self) -> list[User]:
        result = await self.session.execute(
            select(User).where(User.role == UserRole.MODERATOR, User.is_active.is_(True))
        )
        return list(result.scalars())

    async def list_staff(self) -> list[User]:
        result = await self.session.execute(select(User).where(User.is_active.is_(True)))
        return list(result.scalars())

    async def upsert_user(
        self,
        telegram_id: int,
        role: UserRole,
        username: str | None = None,
        full_name: str | None = None,
    ) -> User:
        user = await self.get_by_telegram_id(telegram_id)
        if user:
            user.role = role.value
            user.username = username or user.username
            user.full_name = full_name or user.full_name
            user.is_active = True
            return user
        user = User(
            telegram_id=telegram_id,
            username=username,
            full_name=full_name,
            role=role.value,
            is_active=True,
        )
        self.session.add(user)
        await self.session.flush()
        return user

    async def deactivate_moderator(self, telegram_id: int) -> bool:
        user = await self.get_by_telegram_id(telegram_id)
        if not user or user.role != UserRole.MODERATOR:
            return False
        user.is_active = False
        await self.session.flush()
        return True


async def seed_initial_admins(session: AsyncSession, admin_ids: set[int]) -> None:
    repo = UserRepository(session)
    for telegram_id in admin_ids:
        await repo.upsert_user(telegram_id=telegram_id, role=UserRole.ADMIN)

