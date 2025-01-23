from pydantic_settings import BaseSettings, SettingsConfigDict
from loguru import logger

from pathlib import Path
import os


class BaseSettingsWithConfig(BaseSettings):
    """Родительский класс с настройками .env и экстра-атрибутов.
    Нужен, чтобы унаследовать эти настройки для всех классов настроек дальше"""

    # Определяем абсолютный путь к файлу .env
    env_path: str = os.path.join(Path(__file__).parent.parent.absolute(), ".env")
    logger.debug(env_path)

    model_config = SettingsConfigDict(
        env_file=env_path, env_file_encoding="utf-8", extra="allow"
    )


class Settings(BaseSettingsWithConfig):
    """Модель настроек"""
    # Креды гигачата
    gigachat_api_token: str
    max_tokens_assessment: int
    max_tokens_answer: int
    alpha_coefficient: float

    # Креды Telegram
    tg_token: str
    admin_chat_id: int
    skip_updates: bool = True

    # Креды базы
    db_name: str
    db_user: str
    db_password: str
    db_host: str

    # Креды Redis
    redis_host: str
    redis_port: int
    redis_count_db: str


settings = Settings()
