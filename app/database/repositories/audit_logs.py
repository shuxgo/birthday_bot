from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import AuditLog


class AuditRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def log(
        self,
        user_id: int | None,
        action: str,
        entity_type: str | None = None,
        entity_id: int | None = None,
        payload: dict | None = None,
    ) -> None:
        self.session.add(
            AuditLog(
                user_id=user_id,
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                payload=payload,
            )
        )

