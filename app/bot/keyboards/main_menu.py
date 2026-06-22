from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from app.database.models import UserRole


def main_menu(role: str) -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text="🎂 Новый именинник"), KeyboardButton(text="📅 Готовые к публикации")],
        [KeyboardButton(text="📝 Мои черновики"), KeyboardButton(text="ℹ️ Помощь")],
    ]
    if role == UserRole.ADMIN:
        buttons.insert(1, [KeyboardButton(text="👥 Модераторы"), KeyboardButton(text="📣 Настройки канала")])
        buttons.insert(2, [KeyboardButton(text="🖼 Промт для фото"), KeyboardButton(text="✍️ Промт для текста")])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
