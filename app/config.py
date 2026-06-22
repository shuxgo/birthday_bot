from functools import lru_cache
from zoneinfo import ZoneInfo

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: str = Field(alias="BOT_TOKEN")
    database_url: str = Field(alias="DATABASE_URL")
    redis_url: str = Field(alias="REDIS_URL")
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_text_model: str = Field(default="gpt-4.1-mini", alias="OPENAI_TEXT_MODEL")
    openai_image_model: str = Field(default="gpt-image-1", alias="OPENAI_IMAGE_MODEL")
    timezone: str = Field(default="Asia/Tashkent", alias="TIMEZONE")
    initial_admin_ids: str = Field(default="", alias="INITIAL_ADMIN_IDS")
    default_company_name: str = Field(default="Company", alias="DEFAULT_COMPANY_NAME")
    default_company_style: str = Field(default="corporate, warm, modern", alias="DEFAULT_COMPANY_STYLE")
    public_base_url: str = Field(default="", alias="PUBLIC_BASE_URL")
    channel_id: str = Field(default="", alias="CHANNEL_ID")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def tz(self) -> ZoneInfo:
        return ZoneInfo(self.timezone)

    @property
    def admin_ids(self) -> set[int]:
        return {int(x.strip()) for x in self.initial_admin_ids.split(",") if x.strip()}


@lru_cache
def get_settings() -> Settings:
    return Settings()

