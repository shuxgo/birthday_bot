import logging
from datetime import datetime

from aiogram import Bot
from aiogram.types import FSInputFile, InputMediaPhoto
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import BirthdayPost, PostStatus, PublicationLog

logger = logging.getLogger(__name__)


class PostPublicationService:
    def __init__(self, bot: Bot, session: AsyncSession, channel_id: str):
        self.bot = bot
        self.session = session
        self.channel_id = channel_id

    async def publish(self, post: BirthdayPost) -> None:
        if post.published_at:
            return
        if not self.channel_id:
            raise RuntimeError("Канал для публикации не настроен")

        message_ids: list[int] = []
        photos = [member.person for member in sorted(post.members, key=lambda item: item.sort_order)]
        if not photos:
            raise RuntimeError("В посте нет участников")

        if len(photos) == 1:
            person = photos[0]
            photo = self._photo_input(person.generated_photo_path, person.generated_photo_file_id)
            msg = await self.bot.send_photo(self.channel_id, photo=photo, caption=post.text)
            message_ids.append(msg.message_id)
        else:
            media = [
                InputMediaPhoto(media=self._photo_input(p.generated_photo_path, p.generated_photo_file_id))
                for p in photos
            ]
            messages = await self.bot.send_media_group(self.channel_id, media=media)
            message_ids.extend(message.message_id for message in messages)
            text_msg = await self.bot.send_message(self.channel_id, post.text or "")
            message_ids.append(text_msg.message_id)

        post.status = PostStatus.PUBLISHED
        post.published_at = datetime.now(post.publication_datetime.tzinfo)
        self.session.add(
            PublicationLog(
                post_id=post.id,
                channel_id=str(self.channel_id),
                telegram_message_ids=message_ids,
                status="published",
            )
        )
        await self.session.flush()

    @staticmethod
    def _photo_input(path: str | None, file_id: str | None):
        if path:
            return FSInputFile(path)
        if file_id:
            return file_id
        raise RuntimeError("У участника нет сгенерированного фото")

