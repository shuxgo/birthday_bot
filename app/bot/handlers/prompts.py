from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.states.prompts import PromptFlow
from app.database.models import PromptType, UserRole
from app.database.repositories.prompts import PromptRepository

router = Router()


@router.message(F.text.in_({"Промт для фото", "Промт для текста"}))
async def show_prompt(message: Message, session: AsyncSession, db_user) -> None:
    if db_user.role != UserRole.ADMIN:
        await message.answer("Эта настройка доступна только администратору.")
        return
    prompt_type = PromptType.IMAGE if message.text == "Промт для фото" else PromptType.TEXT
    prompt = await PromptRepository(session).get_active(prompt_type)
    await message.answer(
        f"Текущий промт v{prompt.version if prompt else 0}:\n\n{prompt.content if prompt else 'не задан'}\n\n"
        "Чтобы изменить, отправьте: изменить промт"
    )


@router.message(F.text.lower() == "изменить промт")
async def ask_prompt(message: Message, state: FSMContext) -> None:
    await state.set_state(PromptFlow.waiting_text_prompt)
    await message.answer("Отправьте новый текстовый промт. Для фото используйте команду: изменить фото промт")


@router.message(F.text.lower() == "изменить фото промт")
async def ask_image_prompt(message: Message, state: FSMContext) -> None:
    await state.set_state(PromptFlow.waiting_image_prompt)
    await message.answer("Отправьте новый промт для генерации фото.")


@router.message(PromptFlow.waiting_text_prompt)
async def save_text_prompt(message: Message, state: FSMContext, session: AsyncSession, db_user) -> None:
    await PromptRepository(session).create_version(PromptType.TEXT, message.text, db_user.id)
    await state.clear()
    await message.answer("Промт для текста сохранён новой версией.")


@router.message(PromptFlow.waiting_image_prompt)
async def save_image_prompt(message: Message, state: FSMContext, session: AsyncSession, db_user) -> None:
    await PromptRepository(session).create_version(PromptType.IMAGE, message.text, db_user.id)
    await state.clear()
    await message.answer("Промт для фото сохранён новой версией.")

