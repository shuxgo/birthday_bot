from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def preview_keyboard(post_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Регенерация последнего фото", callback_data=f"post:regen:{post_id}")],
            [InlineKeyboardButton(text="Изменить текст", callback_data=f"post:text:{post_id}")],
            [InlineKeyboardButton(text="Дата публикации", callback_data=f"post:date:{post_id}")],
            [InlineKeyboardButton(text="Подтвердить", callback_data=f"post:approve:{post_id}")],
            [InlineKeyboardButton(text="Отменить", callback_data=f"post:cancel:{post_id}")],
        ]
    )


def back_cancel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Назад", callback_data="flow:back"),
                InlineKeyboardButton(text="Отменить", callback_data="flow:cancel"),
            ]
        ]
    )

