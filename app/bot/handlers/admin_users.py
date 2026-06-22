from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards.inline import back_cancel_keyboard, moderators_keyboard
from app.bot.keyboards.main_menu import main_menu
from app.bot.states.admin import AdminFlow
from app.database.models import UserRole
from app.database.repositories.users import UserRepository
from app.utils.validators import parse_telegram_id

router = Router()


async def _moderators_text(session: AsyncSession) -> str:
    moderators = await UserRepository(session).list_moderators()
    lines = ["👥 Модераторы:"]
    if moderators:
        lines.extend(f"• {u.telegram_id} @{u.username or '-'}" for u in moderators)
    else:
        lines.append("Пока нет добавленных модераторов.")
    return "\n".join(lines)


@router.message(F.text.in_({"👥 Модераторы", "Модераторы"}))
async def moderators_menu(message: Message, session: AsyncSession, db_user) -> None:
    if db_user.role != UserRole.ADMIN:
        await message.answer("Доступно только администратору.")
        return
    await message.answer(await _moderators_text(session), reply_markup=moderators_keyboard())


@router.callback_query(F.data == "moderators:list")
async def refresh_moderators(callback: CallbackQuery, session: AsyncSession, db_user) -> None:
    if db_user.role != UserRole.ADMIN:
        await callback.answer("Доступно только администратору.", show_alert=True)
        return
    await callback.message.edit_text(await _moderators_text(session), reply_markup=moderators_keyboard())
    await callback.answer()


@router.callback_query(F.data == "moderators:add")
async def ask_moderator_id_callback(callback: CallbackQuery, state: FSMContext, db_user) -> None:
    if db_user.role != UserRole.ADMIN:
        await callback.answer("Доступно только администратору.", show_alert=True)
        return
    await state.set_state(AdminFlow.waiting_moderator_id)
    await callback.message.answer("Введите Telegram ID модератора.", reply_markup=back_cancel_keyboard())
    await callback.answer()


@router.message(AdminFlow.waiting_moderator_id)
async def add_moderator(message: Message, state: FSMContext, session: AsyncSession, db_user) -> None:
    try:
        telegram_id = parse_telegram_id(message.text)
    except ValueError as exc:
        await message.answer(str(exc), reply_markup=back_cancel_keyboard())
        return
    await UserRepository(session).upsert_user(telegram_id, UserRole.MODERATOR)
    await state.clear()
    await message.answer("✅ Модератор добавлен.", reply_markup=main_menu(db_user.role))
    await message.answer(await _moderators_text(session), reply_markup=moderators_keyboard())


@router.callback_query(F.data == "moderators:remove")
async def ask_remove_moderator(callback: CallbackQuery, state: FSMContext, db_user) -> None:
    if db_user.role != UserRole.ADMIN:
        await callback.answer("Доступно только администратору.", show_alert=True)
        return
    await state.set_state(AdminFlow.waiting_remove_moderator_id)
    await callback.message.answer("Введите Telegram ID модератора для удаления.", reply_markup=back_cancel_keyboard())
    await callback.answer()


@router.message(AdminFlow.waiting_remove_moderator_id)
async def remove_moderator(message: Message, state: FSMContext, session: AsyncSession, db_user) -> None:
    try:
        telegram_id = parse_telegram_id(message.text)
    except ValueError as exc:
        await message.answer(str(exc), reply_markup=back_cancel_keyboard())
        return
    removed = await UserRepository(session).deactivate_moderator(telegram_id)
    await state.clear()
    if removed:
        await message.answer("🗑 Модератор удалён.", reply_markup=main_menu(db_user.role))
    else:
        await message.answer("Модератор с таким ID не найден.", reply_markup=main_menu(db_user.role))
    await message.answer(await _moderators_text(session), reply_markup=moderators_keyboard())
