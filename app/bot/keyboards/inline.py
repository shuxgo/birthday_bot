from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def preview_keyboard(post_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Регенерация последнего фото", callback_data=f"post:regen:{post_id}")],
            [InlineKeyboardButton(text="✍️ Изменить текст", callback_data=f"post:text:{post_id}")],
            [InlineKeyboardButton(text="🕘 Дата публикации", callback_data=f"post:date:{post_id}")],
            [InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"post:approve:{post_id}")],
            [InlineKeyboardButton(text="❌ Отменить", callback_data=f"post:cancel:{post_id}")],
        ]
    )


def back_cancel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⬅️ Назад", callback_data="flow:back"),
                InlineKeyboardButton(text="❌ Отменить", callback_data="flow:cancel"),
            ]
        ]
    )


def moderators_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Добавить модератора", callback_data="moderators:add")],
            [InlineKeyboardButton(text="🗑 Удалить модератора", callback_data="moderators:remove")],
            [InlineKeyboardButton(text="🔄 Обновить список", callback_data="moderators:list")],
            [InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="menu:back")],
        ]
    )


def channel_settings_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✏️ Изменить канал", callback_data="channel:edit")],
            [InlineKeyboardButton(text="✅ Проверить права бота", callback_data="channel:check")],
            [InlineKeyboardButton(text="📨 Отправить тест", callback_data="channel:test")],
            [InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="menu:back")],
        ]
    )


def prompt_keyboard(prompt_type: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✏️ Изменить промт", callback_data=f"prompt:edit:{prompt_type}")],
            [InlineKeyboardButton(text="👁 Показать текущий", callback_data=f"prompt:show:{prompt_type}")],
            [InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="menu:back")],
        ]
    )


def ready_posts_keyboard(post_ids: list[int]) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=f"📄 Открыть пост #{post_id}", callback_data=f"ready:show:{post_id}")]
        for post_id in post_ids
    ]
    rows.append([InlineKeyboardButton(text="🔄 Обновить список", callback_data="ready:list")])
    rows.append([InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="menu:back")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
