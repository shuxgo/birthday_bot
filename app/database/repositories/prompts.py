from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import PromptTemplate, PromptType

DEFAULT_IMAGE_PROMPT = """Создай поздравительное корпоративное изображение по фото сотрудника.
Стиль: {company_style}.
Сохрани узнаваемость человека, сделай праздничный аккуратный фон.
Данные: {full_name}, {position}, {branch}, дата рождения {birth_date}.
Язык визуальных надписей: {language}.
Требования к фото: {photo_requirements}."""

DEFAULT_TEXT_PROMPT = """Напиши теплое корпоративное поздравление с днем рождения.
Именинники:
{persons_list}
Дата публикации: {date}.
Компания: {company_name}.
Тон: {tone}.
Язык: {language}.
Не искажай ФИО, должности и филиалы. Без чрезмерной официальности."""


class PromptRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_active(self, prompt_type: PromptType) -> PromptTemplate | None:
        result = await self.session.execute(
            select(PromptTemplate)
            .where(PromptTemplate.type == prompt_type.value, PromptTemplate.is_active.is_(True))
            .order_by(PromptTemplate.version.desc())
        )
        return result.scalars().first()

    async def create_version(
        self, prompt_type: PromptType, content: str, created_by: int | None
    ) -> PromptTemplate:
        max_version = await self.session.scalar(
            select(func.max(PromptTemplate.version)).where(PromptTemplate.type == prompt_type.value)
        )
        await self.session.execute(
            update(PromptTemplate)
            .where(PromptTemplate.type == prompt_type.value)
            .values(is_active=False)
        )
        prompt = PromptTemplate(
            type=prompt_type.value,
            content=content,
            version=(max_version or 0) + 1,
            is_active=True,
            created_by=created_by,
        )
        self.session.add(prompt)
        await self.session.flush()
        return prompt

    async def ensure_defaults(self) -> None:
        for prompt_type, content in (
            (PromptType.IMAGE, DEFAULT_IMAGE_PROMPT),
            (PromptType.TEXT, DEFAULT_TEXT_PROMPT),
        ):
            if not await self.get_active(prompt_type):
                await self.create_version(prompt_type, content, None)

