from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.bot.keyboards.main_menu import main_menu

router = Router()


@router.message(CommandStart())
async def start(message: Message, db_user) -> None:
    await message.answer(
        "Бот поздравлений готов к работе. Выберите действие в меню.",
        reply_markup=main_menu(db_user.role),
    )


@router.message(lambda m: m.text == "Помощь")
async def help_message(message: Message) -> None:
    await message.answer(
        "Создайте именинника, проверьте предпросмотр и подтвердите публикацию. "
        "Все даты указываются по часовому поясу Asia/Tashkent."
    )

