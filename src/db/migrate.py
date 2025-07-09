from playhouse.migrate import PostgresqlMigrator, migrate
from src.db.db import db
from src.db.models import Users, Subscriptions
from src.bot.bot_content import basics
import peewee
import datetime
from loguru import logger

# Создаем мигратор
migrator = PostgresqlMigrator(db)


def run_migrations():
    logger.info('Начинаю миграции')
    db.connect()

    # Проверка таблицы Users
    if not Users.table_exists():
        db.create_tables([Users])
    else:
        logger.info('Проверяем наличие колонок в таблице users')
        # Получение списка колонок напрямую из базы
        columns = [col.name for col in db.get_columns('users')]

        # Удаление поля 'paid', если оно существует
        delete_field_name = 'paid'
        if delete_field_name in columns:
            logger.info('Поле paid найдено, удаляем его')
            migrate(
                migrator.drop_column('users', delete_field_name)
            )
        else:
            logger.info('Поле paid не найдено, пропускаем удаление')

        # Добавление поля 'created_at', если оно отсутствует
        if 'created_at' not in columns:
            logger.info('Поле created_at отсутствует, добавляем его')
            migrate(
                migrator.add_column('users', 'created_at', peewee.DateTimeField(default=datetime.datetime.now))
            )
        else:
            logger.info('Поле created_at уже существует, пропускаем добавление')

    # Проверка таблицы Subscriptions
    if not Subscriptions.table_exists():
        db.create_tables([Subscriptions])
        # Создание подписок для каждого пользователя
        for user in Users.select():
            Subscriptions.create(user_id=user.id,
                                 status=basics.SubscriptionStatus().inactive)

    db.close()


if __name__ == "__main__":
    run_migrations()
