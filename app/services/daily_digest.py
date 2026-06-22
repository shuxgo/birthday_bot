from datetime import datetime, timedelta

from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.posts import PostRepository
from app.database.repositories.users import UserRepository
from app.utils.dates import format_dt


async def send_daily_digest(bot: Bot, session: AsyncSession, now: datetime) -> None:
    posts = await PostRepository(session).list_ready()
    staff = await UserRepository(session).list_staff()
    end = now + timedelta(days=3)
    relevant = [p for p in posts if now <= p.publication_datetime <= end]

    lines = ["Публикации на ближайшие 3 дня:"]
    for offset in range(3):
        day = (now + timedelta(days=offset)).date()
        day_posts = [p for p in relevant if p.publication_datetime.date() == day]
        lines.append("")
        lines.append(day.strftime("%d.%m.%Y"))
        if not day_posts:
            lines.append("— нет публикаций")
        for post in day_posts:
            lines.append(format_dt(post.publication_datetime))
            for member in sorted(post.members, key=lambda item: item.sort_order):
                lines.append(f"— {member.person.full_name}")

    text = "\n".join(lines)
    for user in staff:
        await bot.send_message(user.telegram_id, text)

