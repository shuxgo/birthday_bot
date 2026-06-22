from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models import (
    BirthdayPerson,
    BirthdayPost,
    BirthdayPostMember,
    PostStatus,
)


class PostRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_person(
        self,
        *,
        full_name: str,
        position: str,
        branch: str,
        birth_date,
        original_photo_file_id: str,
        generated_photo_path: str | None,
        generated_photo_file_id: str | None,
        created_by: int,
    ) -> BirthdayPerson:
        person = BirthdayPerson(
            full_name=full_name,
            position=position,
            branch=branch,
            birth_date=birth_date,
            original_photo_file_id=original_photo_file_id,
            generated_photo_path=generated_photo_path,
            generated_photo_file_id=generated_photo_file_id,
            created_by=created_by,
        )
        self.session.add(person)
        await self.session.flush()
        return person

    async def find_post_for_day(self, publication_datetime: datetime) -> BirthdayPost | None:
        day_start = publication_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        result = await self.session.execute(
            select(BirthdayPost)
            .options(selectinload(BirthdayPost.members).selectinload(BirthdayPostMember.person))
            .where(
                BirthdayPost.publication_datetime >= day_start,
                BirthdayPost.publication_datetime < day_end,
                BirthdayPost.status.notin_([PostStatus.CANCELLED, PostStatus.PUBLISHED]),
            )
            .order_by(BirthdayPost.created_at.asc())
        )
        return result.scalars().first()

    async def get_post(self, post_id: int) -> BirthdayPost | None:
        result = await self.session.execute(
            select(BirthdayPost)
            .options(selectinload(BirthdayPost.members).selectinload(BirthdayPostMember.person))
            .where(BirthdayPost.id == post_id)
        )
        return result.scalar_one_or_none()

    async def list_ready(self) -> list[BirthdayPost]:
        result = await self.session.execute(
            select(BirthdayPost)
            .options(selectinload(BirthdayPost.members).selectinload(BirthdayPostMember.person))
            .where(
                BirthdayPost.status.in_(
                    [PostStatus.PREVIEW, PostStatus.APPROVED, PostStatus.SCHEDULED]
                )
            )
            .order_by(BirthdayPost.publication_datetime.asc())
        )
        return list(result.scalars().unique())

    async def list_due(self, now: datetime, limit: int = 10) -> list[BirthdayPost]:
        result = await self.session.execute(
            select(BirthdayPost)
            .options(selectinload(BirthdayPost.members).selectinload(BirthdayPostMember.person))
            .where(
                BirthdayPost.publication_datetime <= now,
                BirthdayPost.published_at.is_(None),
                BirthdayPost.status.in_([PostStatus.APPROVED, PostStatus.SCHEDULED]),
            )
            .order_by(BirthdayPost.publication_datetime.asc())
            .limit(limit)
            .with_for_update(skip_locked=True)
        )
        return list(result.scalars().unique())

    async def add_person_to_post(
        self, post: BirthdayPost, person: BirthdayPerson, created_by: int
    ) -> BirthdayPost:
        next_order = len(post.members) + 1
        self.session.add(
            BirthdayPostMember(post_id=post.id, person_id=person.id, sort_order=next_order)
        )
        post.status = PostStatus.PREVIEW
        post.approved_by = None
        await self.session.flush()
        return post

    async def create_post_with_person(
        self, publication_datetime: datetime, timezone: str, person: BirthdayPerson, created_by: int
    ) -> BirthdayPost:
        post = BirthdayPost(
            publication_datetime=publication_datetime,
            timezone=timezone,
            status=PostStatus.PREVIEW,
            created_by=created_by,
        )
        self.session.add(post)
        await self.session.flush()
        self.session.add(BirthdayPostMember(post_id=post.id, person_id=person.id, sort_order=1))
        await self.session.flush()
        return await self.get_post(post.id) or post

    async def approve(self, post: BirthdayPost, approved_by: int) -> None:
        post.status = PostStatus.SCHEDULED
        post.approved_by = approved_by
        await self.session.flush()

    async def cancel(self, post: BirthdayPost) -> None:
        post.status = PostStatus.CANCELLED
        await self.session.flush()

