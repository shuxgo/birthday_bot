from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.states.admin import AdminFlow
from app.database.models import UserRole
from app.database.repositories.users import UserRepository
from app.utils.validators import parse_telegram_id

router = Router()


@router.message(F.text == "Модераторы")
async def moderators_menu(message: Message, session: AsyncSession, db_user) -> None:
    if db_user.role != UserRole.ADMIN:
        await message.answer("Доступно только администратору.")
        return
    moderators = await UserRepository(session).list_moderators()
    lines = ["Модераторы:"]
    lines.extend(f"- {u.telegram_id} @{u.username or '-'}" for u in moderators)
    lines.append("\nЧтобы добавить модератора, отправьте: добавить модератора")
    await message.answer("\n".join(lines))


@router.message(F.text.lower() == "добавить модератора")
async def ask_moderator_id(message: Message, state: FSMContext, db_user) -> None:
    if db_user.role != UserRole.ADMIN:
        await message.answer("Доступно только администратору.")
        return
    await state.set_state(AdminFlow.waiting_moderator_id)
    await message.answer("Введите Telegram ID модератора.")


@router.message(AdminFlow.waiting_moderator_id)
async def add_moderator(message: Message, state: FSMContext, session: AsyncSession) -> None:
    try:
        telegram_id = parse_telegram_id(message.text)
    except ValueError as exc:
        await message.answer(str(exc))
        return
    await UserRepository(session).upsert_user(telegram_id, UserRole.MODERATOR)
    await state.clear()
    await message.answer("Модератор добавлен.")

