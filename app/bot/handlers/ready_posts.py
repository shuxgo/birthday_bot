from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards.inline import preview_keyboard, ready_posts_keyboard
from app.database.repositories.posts import PostRepository
from app.services.post_builder import PostBuilder
from app.utils.dates import format_dt

router = Router()


async def _ready_posts_text(session: AsyncSession) -> tuple[str, list[int]]:
    posts = await PostRepository(session).list_ready()
    if not posts:
        return "📅 Готовых публикаций пока нет.", []
    lines = ["Готовые публикации:"]
    for post in posts:
        names = ", ".join(m.person.full_name for m in post.members)
        lines.append(f"#{post.id} {format_dt(post.publication_datetime)} — {names} — {post.status}")
    return "\n".join(lines), [post.id for post in posts]


@router.message(F.text.in_({"📅 Готовые к публикации", "Готовые к публикации"}))
async def ready_posts(message: Message, session: AsyncSession) -> None:
    text, post_ids = await _ready_posts_text(session)
    await message.answer(text, reply_markup=ready_posts_keyboard(post_ids))


@router.callback_query(F.data == "ready:list")
async def ready_posts_callback(callback: CallbackQuery, session: AsyncSession) -> None:
    text, post_ids = await _ready_posts_text(session)
    await callback.message.edit_text(text, reply_markup=ready_posts_keyboard(post_ids))
    await callback.answer()


@router.callback_query(F.data.startswith("ready:show:"))
async def show_post_callback(callback: CallbackQuery, session: AsyncSession) -> None:
    post_id = int(callback.data.rsplit(":", 1)[1])
    post = await PostRepository(session).get_post(post_id)
    if not post:
        await callback.answer("Пост не найден.", show_alert=True)
        return
    await callback.message.answer(PostBuilder.preview_text(post), reply_markup=preview_keyboard(post.id))
    await callback.answer()


@router.message(F.text.regexp(r"^#\d+$"))
async def show_post_by_id(message: Message, session: AsyncSession) -> None:
    post_id = int(message.text[1:])
    post = await PostRepository(session).get_post(post_id)
    if not post:
        await message.answer("Пост не найден.")
        return
    await message.answer(PostBuilder.preview_text(post), reply_markup=preview_keyboard(post.id))
