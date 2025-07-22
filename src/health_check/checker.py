from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import timezone
from src.giga_chat import giga_chat
from src.db.cache import cache
from loguru import logger
from src.config import settings
from aiogram import Bot
from src.db import db
from functools import partial


async def send_health_check(bot: Bot):
    """Отправляет сообщение о статусе бота в чат администратора."""
    status = []

    # Проверяем Redis
    try:
        await cache.cache.set("test", "test")
        await cache.cache.delete("test")
        logger.info("Redis работает корректно")
        status.append("✅ Redis работает")
    except Exception as e:
        logger.error("Redis не работает")
        status.append(f"❌ Redis не работает: {e}")

    # Проверяем GigaChat
    try:
        answer = await giga_chat.get_assessment_of_answer("Ты работаешь? Напиши: да или нет")
        logger.info("GigaChat работает корректно")
        status.append(f"✅ GigaChat работает: '{answer}'")
    except Exception as e:
        logger.error("GigaChat не работает")
        status.append(f"❌ GigaChat не работает: {e}")

    # Проверяем БД
    try:
        await db.get_user(settings.admin_chat_id)
        status.append("✅ База данных работает")
        status.append(f"👥 Количество пользователей: {len(await db.get_users())}")
        logger.info("База данных работает корректно")
    except Exception as e:
        logger.error("База данных не работает")
        status.append(f"❌ База данных не работает: {e}")

    await bot.send_message(settings.admin_chat_id, "📅 Регулярный health-check:\n" + "\n".join(status))
    logger.info("Health-check сообщение отправлено")


def setup_scheduler(bot: Bot):
    """Настройка планировщика задач."""
    scheduler = AsyncIOScheduler(timezone=timezone('Europe/Moscow'))
    scheduler.add_job(
        partial(send_health_check, bot),
        trigger='cron',
        hour=9,
        minute=0
    )
    scheduler.start()
