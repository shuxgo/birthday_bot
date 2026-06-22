from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Setting


class SettingsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, key: str, default=None):
        setting = await self.session.get(Setting, key)
        return default if setting is None else setting.value

    async def set(self, key: str, value) -> Setting:
        setting = await self.session.get(Setting, key)
        if setting:
            setting.value = value
        else:
            setting = Setting(key=key, value=value)
            self.session.add(setting)
        await self.session.flush()
        return setting

