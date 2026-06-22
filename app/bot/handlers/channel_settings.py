from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.states.admin import AdminFlow
from app.database.models import UserRole
from app.database.repositories.settings import SettingsRepository

router = Router()


@router.message(F.text == "Настройки канала")
async def channel_menu(message: Message, session: AsyncSession, db_user) -> None:
    if db_user.role != UserRole.ADMIN:
        await message.answer("Доступно только администратору.")
        return
    channel_id = await SettingsRepository(session).get("channel_id", "не задан")
    await message.answer(
        f"Текущий канал: {channel_id}\nЧтобы изменить, отправьте: изменить канал"
    )


@router.message(F.text.lower() == "изменить канал")
async def ask_channel(message: Message, state: FSMContext, db_user) -> None:
    if db_user.role != UserRole.ADMIN:
        await message.answer("Доступно только администратору.")
        return
    await state.set_state(AdminFlow.waiting_channel_id)
    await message.answer("Введите ID канала или @username. Бот должен быть администратором канала.")


@router.message(AdminFlow.waiting_channel_id)
async def save_channel(message: Message, state: FSMContext, session: AsyncSession, bot: Bot) -> None:
    channel_id = message.text.strip()
    try:
        me = await bot.get_me()
        member = await bot.get_chat_member(channel_id, me.id)
        if member.status not in {"administrator", "creator"}:
            await message.answer("Бот найден в канале, но не является администратором.")
            return
    except Exception as exc:
        await message.answer(f"Не удалось проверить канал: {exc}")
        return
    await SettingsRepository(session).set("channel_id", channel_id)
    await state.clear()
    await message.answer("Канал сохранён.")

