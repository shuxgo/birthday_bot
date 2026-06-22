from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings
from app.database.models import BirthdayPost, PromptType
from app.database.repositories.posts import PostRepository
from app.database.repositories.prompts import PromptRepository
from app.services.prompt_renderer import SafePromptRenderer
from app.services.text_generation import TextGenerationService


class PostBuilder:
    def __init__(self, session: AsyncSession, settings: Settings):
        self.session = session
        self.settings = settings
        self.posts = PostRepository(session)
        self.prompts = PromptRepository(session)
        self.renderer = SafePromptRenderer()
        self.text_generation = TextGenerationService(settings)

    async def attach_person_and_refresh_text(self, person, publication_datetime: datetime, user_id: int):
        post = await self.posts.find_post_for_day(publication_datetime)
        if post:
            await self.posts.add_person_to_post(post, person, user_id)
            post = await self.posts.get_post(post.id) or post
        else:
            post = await self.posts.create_post_with_person(
                publication_datetime, self.settings.timezone, person, user_id
            )
        if not post.text_is_manual:
            post.text = await self.generate_text(post)
        return post

    async def generate_text(self, post: BirthdayPost) -> str:
        prompt = await self.prompts.get_active(PromptType.TEXT)
        if not prompt:
            raise RuntimeError("Промт для текста не настроен")
        persons = sorted(post.members, key=lambda member: member.sort_order)
        persons_list = "\n".join(
            f"- {m.person.full_name}, {m.person.position}, {m.person.branch}" for m in persons
        )
        rendered = self.renderer.render(
            prompt.content,
            {
                "persons_list": persons_list,
                "date": post.publication_datetime.strftime("%d.%m.%Y"),
                "company_name": self.settings.default_company_name,
                "tone": "корпоративный, теплый, уважительный",
                "language": "ru",
            },
        )
        return await self.text_generation.generate(rendered)

    @staticmethod
    def preview_text(post: BirthdayPost) -> str:
        names = ", ".join(m.person.full_name for m in sorted(post.members, key=lambda x: x.sort_order))
        return (
            f"Публикация: {post.publication_datetime.strftime('%d.%m.%Y %H:%M')}\n"
            f"Именинники: {names}\n\n"
            f"{post.text or ''}"
        )

