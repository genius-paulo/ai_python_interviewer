import peewee_async
from loguru import logger

from src.config import settings
from src.db.models import DBModel, Users, Subscriptions, database_proxy
from src.bot.bot_content.basics import Modes, SubscriptionStatus

from src.db.cache.cache import cache
from src.bot.utils import get_skill_map_name
import datetime


db = peewee_async.PooledPostgresqlDatabase(database=settings.db_name,
                                           user=settings.db_user,
                                           password=settings.db_password,
                                           host=settings.db_host)
# Привязываем базу данных к прокси
database_proxy.initialize(db)


async def create_tables(table: DBModel):
    db.create_tables([table])


async def get_table(table: DBModel):
    return await table.select()


async def get_user(tg_id: int):
    user = Users.get(Users.tg_id == tg_id)
    return user


async def get_users() -> list[Users]:
    all_users = Users.select()
    return all_users


async def create_user(tg_id: int):
    # Создаем пользователя
    user = Users(tg_id=tg_id)
    user.save()

    # Создаем запись о подписке для пользователя
    subscription = Subscriptions(
        user_id=user.id,
        status=SubscriptionStatus().inactive,  # По умолчанию подписка неактивна
        start_date=None,
        end_date=None,
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now(),
    )
    subscription.save()

    return user


async def update_mode(tg_id: int, mode: str):
    user = Users.get(Users.tg_id == tg_id)
    user.mode = mode
    user.save()


async def update_skill(tg_id: int, skill: str) -> Users:
    user = Users.get(Users.tg_id == tg_id)
    user.skill = skill
    user.mode = Modes().specific
    user.save()
    return user


async def update_skill_rating(tg_id: int, skill: str, rating: int):
    user = Users.get(Users.tg_id == tg_id)
    setattr(user, skill, rating)
    user.save()
    # TODO: Нужно ли как-то отделить логику бд от кэша в одном интерфейсе?
    try:
        image_cache_key = get_skill_map_name(user, mode='key')
        await cache.delete(image_cache_key)
    except Exception as e:
        # TODO: Подумать над  одной точкой обработки ошибок в Redis. Так работает, но никуда не годится
        logger.error(f'Ошибка при удалении кэша карты скиллов: {e}')
    logger.debug('Оценка скилла обновлена, кэш карты скиллов удален')


async def update_subscription(tg_id: int, days_count: int = 31) -> Subscriptions:
    """Обновляем длительность подписки"""
    user = Users.get(Users.tg_id == tg_id)
    # Обновляем строку подписки для пользователя в таблице subscriptions
    user_subscription = Subscriptions.get(Subscriptions.user_id == user.id)
    user_subscription.status = SubscriptionStatus().active
    logger.debug("Проверяем даты подписки")
    # Проверяем: если дата старта пустая, ставим сегодня, если подписка уже есть,
    # то дату старта не меняем, меняем только дату окончания
    if user_subscription.start_date is None:
        user_subscription.start_date = datetime.datetime.now()
        user_subscription.end_date = user_subscription.start_date + datetime.timedelta(days=days_count)
        logger.debug(f'Дата старта пустая {user_subscription.start_date}, ставим сегодня: '
                     f'{user_subscription.start_date=}, {user_subscription.end_date=}')
    else:
        user_subscription.end_date += datetime.timedelta(days=days_count)
        logger.debug(f'Дата старта не пустая, подписка уже активна, '
                     f'добавляем к подписке count_days: {user_subscription.end_date=}')

    user_subscription.updated_at = datetime.datetime.now()
    user_subscription.save()
    return user_subscription


async def check_paid_status(user: Users) -> bool:
    # Получаем значение поля status из таблицы subscriptions, где user_id равняется user.id
    user_subscription = Subscriptions.get(Subscriptions.user_id == user.id)
    if user_subscription.status == SubscriptionStatus().active:
        return True
    else:
        return False


async def check_paid_status_by_tgid(tg_id: int) -> bool:
    user = Users.get(Users.tg_id == tg_id)
    return await check_paid_status(user)


async def get_paid_status_for_profile(user: Users) -> str:
    """Получаем текст для профиля в зависимости от статуса подписки"""
    user_subscription = Subscriptions.get(Subscriptions.user_id == user.id)
    if user_subscription.status == SubscriptionStatus().active:
        return f'продвинутые AI-функции активны до {user_subscription.end_date.strftime("%d.%m.%Y")}'
    else:
        return 'продвинутые AI-функции не активны'
