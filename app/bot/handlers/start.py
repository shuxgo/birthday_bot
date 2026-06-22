from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.bot.keyboards.main_menu import main_menu

router = Router()


@router.message(CommandStart())
async def start(message: Message, db_user) -> None:
    await message.answer(
        "Бот поздравлений готов к работе. Выберите действие в меню.",
        reply_markup=main_menu(db_user.role),
    )


@router.callback_query(F.data == "menu:back")
async def back_to_menu(callback: CallbackQuery, state: FSMContext, db_user) -> None:
    await state.clear()
    await callback.message.answer("Главное меню.", reply_markup=main_menu(db_user.role))
    await callback.answer()


@router.message(F.text.in_({"ℹ️ Помощь", "Помощь"}))
async def help_message(message: Message) -> None:
    await message.answer(
        "Создайте именинника, проверьте предпросмотр и подтвердите публикацию. "
        "Все даты указываются по часовому поясу Asia/Tashkent."
    )


@router.message(F.text.in_({"отмена", "Отмена", "/cancel"}))
async def cancel_by_text(message: Message, state: FSMContext, db_user) -> None:
    await state.clear()
    await message.answer("Действие отменено.", reply_markup=main_menu(db_user.role))
