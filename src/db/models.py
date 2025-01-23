import peewee
import datetime

from src.bot.bot_content import skills, basics

# Создаем пустой Proxy для будущей базы данных
database_proxy = peewee.Proxy()


class DBModel(peewee.Model):
    # Указываем proxy вместо реальной базы данных
    class Meta:
        database = database_proxy


class Users(DBModel):
    """Модель пользователя"""
    id = peewee.AutoField(primary_key=True)
    tg_id = peewee.BigIntegerField(unique=True)

    mode = peewee.CharField(choices=[basics.Modes().all, basics.Modes().specific, basics.Modes().worst],
                            default=basics.Modes().all)
    skill = peewee.TextField(default=skills.Basic().short_name)


    # Оценки скиллов
    basic = peewee.FloatField(default=0.0)
    oop = peewee.FloatField(default=0.0)
    standard_lib = peewee.FloatField(default=0.0)
    async_prog = peewee.FloatField(default=0.0)
    db = peewee.FloatField(default=0.0)
    web = peewee.FloatField(default=0.0)
    test = peewee.FloatField(default=0.0)
    docs = peewee.FloatField(default=0.0)
    devops = peewee.FloatField(default=0.0)
    efficiency = peewee.FloatField(default=0.0)
    additional = peewee.FloatField(default=0.0)
    algorithms = peewee.FloatField(default=0.0)

    created_at = peewee.DateTimeField(default=datetime.datetime.now)


class Subscriptions(DBModel):
    """Модель подписки"""
    id = peewee.AutoField(primary_key=True)
    user_id = peewee.ForeignKeyField(Users, backref='subscriptions')
    start_date = peewee.DateField(null=True)
    end_date = peewee.DateField(null=True)
    status = peewee.CharField(choices=[basics.SubscriptionStatus().active, basics.SubscriptionStatus().inactive])
    created_at = peewee.DateTimeField(default=datetime.datetime.now)
    updated_at = peewee.DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = database_proxy





