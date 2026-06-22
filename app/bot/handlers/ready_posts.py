from aiogram import F, Router
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.posts import PostRepository
from app.services.post_builder import PostBuilder
from app.utils.dates import format_dt

router = Router()


@router.message(F.text == "Готовые к публикации")
async def ready_posts(message: Message, session: AsyncSession) -> None:
    posts = await PostRepository(session).list_ready()
    if not posts:
        await message.answer("Готовых публикаций пока нет.")
        return
    lines = ["Готовые публикации:"]
    for post in posts:
        names = ", ".join(m.person.full_name for m in post.members)
        lines.append(f"#{post.id} {format_dt(post.publication_datetime)} — {names} — {post.status}")
    await message.answer("\n".join(lines))


@router.message(F.text.regexp(r"^#\d+$"))
async def show_post_by_id(message: Message, session: AsyncSession) -> None:
    post_id = int(message.text[1:])
    post = await PostRepository(session).get_post(post_id)
    if not post:
        await message.answer("Пост не найден.")
        return
    await message.answer(PostBuilder.preview_text(post))

