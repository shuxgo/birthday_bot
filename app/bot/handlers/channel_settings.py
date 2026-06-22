from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards.inline import back_cancel_keyboard, channel_settings_keyboard
from app.bot.keyboards.main_menu import main_menu
from app.bot.states.admin import AdminFlow
from app.database.models import UserRole
from app.database.repositories.settings import SettingsRepository

router = Router()


async def _channel_text(session: AsyncSession) -> str:
    channel_id = await SettingsRepository(session).get("channel_id", "не задан")
    return f"📣 Текущий канал: {channel_id}"


@router.message(F.text.in_({"📣 Настройки канала", "Настройки канала"}))
async def channel_menu(message: Message, session: AsyncSession, db_user) -> None:
    if db_user.role != UserRole.ADMIN:
        await message.answer("Доступно только администратору.")
        return
    await message.answer(await _channel_text(session), reply_markup=channel_settings_keyboard())


@router.callback_query(F.data == "channel:edit")
async def ask_channel(callback: CallbackQuery, state: FSMContext, db_user) -> None:
    if db_user.role != UserRole.ADMIN:
        await callback.answer("Доступно только администратору.", show_alert=True)
        return
    await state.set_state(AdminFlow.waiting_channel_id)
    await callback.message.answer(
        "Введите ID канала или @username. Бот должен быть администратором канала.",
        reply_markup=back_cancel_keyboard(),
    )
    await callback.answer()


async def _check_channel(bot: Bot, channel_id: str) -> tuple[bool, str]:
    me = await bot.get_me()
    member = await bot.get_chat_member(channel_id, me.id)
    if member.status not in {"administrator", "creator"}:
        return False, "Бот найден в канале, но не является администратором."
    return True, "✅ Бот является администратором канала."


@router.message(AdminFlow.waiting_channel_id)
async def save_channel(message: Message, state: FSMContext, session: AsyncSession, bot: Bot, db_user) -> None:
    channel_id = message.text.strip()
    try:
        ok, text = await _check_channel(bot, channel_id)
        if not ok:
            await message.answer(text, reply_markup=back_cancel_keyboard())
            return
    except Exception as exc:
        await message.answer(f"Не удалось проверить канал: {exc}", reply_markup=back_cancel_keyboard())
        return
    await SettingsRepository(session).set("channel_id", channel_id)
    await state.clear()
    await message.answer("✅ Канал сохранён.", reply_markup=main_menu(db_user.role))
    await message.answer(await _channel_text(session), reply_markup=channel_settings_keyboard())


@router.callback_query(F.data == "channel:check")
async def check_channel(callback: CallbackQuery, session: AsyncSession, bot: Bot, db_user) -> None:
    if db_user.role != UserRole.ADMIN:
        await callback.answer("Доступно только администратору.", show_alert=True)
        return
    channel_id = await SettingsRepository(session).get("channel_id")
    if not channel_id:
        await callback.answer("Канал не задан.", show_alert=True)
        return
    try:
        ok, text = await _check_channel(bot, channel_id)
        await callback.message.answer(text)
    except Exception as exc:
        await callback.message.answer(f"Не удалось проверить канал: {exc}")
    await callback.answer()


@router.callback_query(F.data == "channel:test")
async def send_test_to_channel(callback: CallbackQuery, session: AsyncSession, bot: Bot, db_user) -> None:
    if db_user.role != UserRole.ADMIN:
        await callback.answer("Доступно только администратору.", show_alert=True)
        return
    channel_id = await SettingsRepository(session).get("channel_id")
    if not channel_id:
        await callback.answer("Канал не задан.", show_alert=True)
        return
    try:
        await bot.send_message(channel_id, "✅ Тестовое сообщение от бота поздравлений DELTA.")
        await callback.message.answer("✅ Тестовое сообщение отправлено.")
    except Exception as exc:
        await callback.message.answer(f"Не удалось отправить тест: {exc}")
    await callback.answer()
