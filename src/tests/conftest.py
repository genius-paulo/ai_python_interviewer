import pytest_asyncio
import peewee_async
from loguru import logger
from src.config import settings
from src.db.models import database_proxy, Users


@pytest_asyncio.fixture(scope="module")
async def db():
    db = peewee_async.PooledPostgresqlDatabase(database=settings.db_name,
                                               user=settings.db_user,
                                               password=settings.db_password,
                                               host=settings.db_host)
    result = database_proxy.initialize(db)
    logger.info(f'Фикстура базы запущена: {result}')
    yield db
    # удаляем тестового пользователя из базы
    Users.delete().where(Users.tg_id == 12345678).execute()
    #db.drop_tables([Users, SkillsScores])


