from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards.inline import back_cancel_keyboard, prompt_keyboard
from app.bot.keyboards.main_menu import main_menu
from app.bot.states.prompts import PromptFlow
from app.database.models import PromptType, UserRole
from app.database.repositories.prompts import PromptRepository

router = Router()


def _prompt_type_from_text(text: str) -> PromptType:
    return PromptType.IMAGE if "фото" in text.lower() else PromptType.TEXT


async def _prompt_text(session: AsyncSession, prompt_type: PromptType) -> str:
    prompt = await PromptRepository(session).get_active(prompt_type)
    title = "🖼 Промт для фото" if prompt_type == PromptType.IMAGE else "✍️ Промт для текста"
    return (
        f"{title}\n"
        f"Текущая версия: v{prompt.version if prompt else 0}\n\n"
        f"{prompt.content if prompt else 'Промт не задан'}"
    )


@router.message(F.text.in_({"🖼 Промт для фото", "✍️ Промт для текста", "Промт для фото", "Промт для текста"}))
async def show_prompt(message: Message, session: AsyncSession, db_user) -> None:
    if db_user.role != UserRole.ADMIN:
        await message.answer("Эта настройка доступна только администратору.")
        return
    prompt_type = _prompt_type_from_text(message.text)
    await message.answer(
        await _prompt_text(session, prompt_type),
        reply_markup=prompt_keyboard(prompt_type.value),
    )


@router.callback_query(F.data.startswith("prompt:show:"))
async def show_prompt_callback(callback: CallbackQuery, session: AsyncSession, db_user) -> None:
    if db_user.role != UserRole.ADMIN:
        await callback.answer("Доступно только администратору.", show_alert=True)
        return
    prompt_type = PromptType(callback.data.rsplit(":", 1)[1])
    await callback.message.edit_text(
        await _prompt_text(session, prompt_type),
        reply_markup=prompt_keyboard(prompt_type.value),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("prompt:edit:"))
async def ask_prompt(callback: CallbackQuery, state: FSMContext, db_user) -> None:
    if db_user.role != UserRole.ADMIN:
        await callback.answer("Доступно только администратору.", show_alert=True)
        return
    prompt_type = callback.data.rsplit(":", 1)[1]
    await state.set_state(
        PromptFlow.waiting_image_prompt if prompt_type == PromptType.IMAGE.value else PromptFlow.waiting_text_prompt
    )
    label = "фото" if prompt_type == PromptType.IMAGE.value else "текста"
    await callback.message.answer(f"Отправьте новый промт для {label}.", reply_markup=back_cancel_keyboard())
    await callback.answer()


@router.message(PromptFlow.waiting_text_prompt)
async def save_text_prompt(message: Message, state: FSMContext, session: AsyncSession, db_user) -> None:
    await PromptRepository(session).create_version(PromptType.TEXT, message.text, db_user.id)
    await state.clear()
    await message.answer("✅ Промт для текста сохранён новой версией.", reply_markup=main_menu(db_user.role))
    await message.answer(await _prompt_text(session, PromptType.TEXT), reply_markup=prompt_keyboard(PromptType.TEXT.value))


@router.message(PromptFlow.waiting_image_prompt)
async def save_image_prompt(message: Message, state: FSMContext, session: AsyncSession, db_user) -> None:
    await PromptRepository(session).create_version(PromptType.IMAGE, message.text, db_user.id)
    await state.clear()
    await message.answer("✅ Промт для фото сохранён новой версией.", reply_markup=main_menu(db_user.role))
    await message.answer(await _prompt_text(session, PromptType.IMAGE), reply_markup=prompt_keyboard(PromptType.IMAGE.value))
