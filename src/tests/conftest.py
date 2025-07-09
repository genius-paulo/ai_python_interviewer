import pytest_asyncio
import peewee_async
from loguru import logger
from src.config import settings
from src.db.models import database_proxy, Users, Subscriptions


@pytest_asyncio.fixture(scope="module")
async def conftest_db():
    # Инициализируем асинхронную базу данных
    conftest_db = peewee_async.PooledPostgresqlDatabase(
        database=settings.db_name,
        user=settings.db_user,
        password=settings.db_password,
        host=settings.db_host
    )

    # Привязываем модели к БД
    database_proxy.initialize(conftest_db)

    logger.info("✅ Подключение к тестовой БД установлено")

    yield conftest_db

    logger.info("🔄 Начало очистки после тестов")

    try:
        # Удаляем тестового пользователя и связанные записи
        with conftest_db.atomic():
    # Получаем id пользователя по tg_id
            user_id_query = Users.select(Users.id).where(Users.tg_id == "12345678")
            # Сначала удаляем связанные подписки
            Subscriptions.delete().where(Subscriptions.user_id.in_(user_id_query)).execute()
            # Потом удаляем пользователя
            Users.delete().where(Users.tg_id == 12345678).execute()
            """Если что-то пошло не так:
            DELETE FROM subscriptions WHERE user_id = (
                SELECT id FROM users WHERE tg_id = '12345678'
            );
            DELETE FROM users WHERE tg_id = '12345678';
            """
        logger.info("🗑 Тестовые данные удалены")
    except Exception as e:
        logger.error(f"❌ Ошибка при очистке тестовых данных: {e}")
    #TODO: Тесты проходят, но  в конце падают с RuntimeError: Event loop is closed. Исправить
