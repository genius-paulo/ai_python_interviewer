from pydantic import BaseModel
from typing import Optional
from src.bot.bot_content import skills
import random
from loguru import logger


class Commands:
    start = 'start'

    get_question_command = 'get_question'
    get_question_text = '❓️Получить вопрос'

    get_answer_command = 'get_answer'
    get_answer_text = '✨ Сгенерировать ответ'

    change_skills_command = 'change_skill'
    change_skills_text = '💪 Выбрать навык'

    profile_command = 'profile'
    profile_text = '👤 Мой профиль'

    change_mode_command = 'mode'
    change_mode_text = '⚙️ Выбрать режим интервью'

    get_subscribe_command = 'get_ai_plus'
    get_subscribe_text = '✨ Получить все возможности AI+'

    another_question_text = '🔁 Другой вопрос'

    cancel_command = 'cancel'
    cancel_text = '🙅Отмена'


class Modes(BaseModel):
    all: str = 'all'
    specific: str = 'specific'
    worst: str = 'worst'


class Stickers(BaseModel):
    """Модель стикеров из Telegram, поделенных на категории: грустные, нейтральные, веселые"""
    sad: list = ['CAACAgIAAxkBAAENeRdngR-0D0fsvNtuvVMkyTUwnG8tdQACY0MAAl4qaUhBsrEwZuLtSjYE',
                 'CAACAgIAAxkBAAENeRlngR_9Nz7usxNa92imry4U00dYyAACoUYAAspVYUgfCcVI2EJH8jYE',
                 'CAACAgIAAxkBAAENeRtngSAdpJUdQa-CknA0jP2C5tCLiAACMEAAAkVDYUhJgUe8OF4vMDYE']
    neutral: list = ['CAACAgIAAxkBAAENeR1ngSAvFZgQxErYDLGoaFVNouO7MgAC5UUAAj3IYEiV-6uLXANTXTYE',
                     'CAACAgIAAxkBAAENeR9ngSB4zITgxUK7yjpmkBBL8V7brwAC0UQAAnf8YEitLhXjRxtXITYE',
                     'CAACAgIAAxkBAAENeSFngSCX3kuZ6QXsLYVytIToSgznWAACaUMAAzZoSJmYdv6yGx3jNgQ']
    happy: list = ['CAACAgIAAxkBAAENcc1neRshUdHxcJ35z_hCsZzRpy6zBwACtUMAAuWBYUjP53LZfBfr2TYE',
                   'CAACAgIAAxkBAAENeSVngSDBXkJLjkA5eJH26qKtYQMDuwACJD8AAlUDaEgBW9n4mcteezYE',
                   'CAACAgIAAxkBAAENeSdngSDNsUfvkoBsvuZJgHFTV5IG1gACyUYAAnZZYUi17hfzGM_6FjYE',
                   'CAACAgIAAxkBAAENeSlngSEBa8HGVwoSuTH58P8cYDTQqgACKkcAAmHaaEirAAENkFgUrmg2BA']

    @classmethod
    def get_sad_sticker(cls):
        logger.debug('Возвращаем рандомный стикер из категории sad')
        return random.choice(cls().sad)

    @classmethod
    def get_neutral_sticker(cls):
        logger.debug('Возвращаем рандомный стикер из категории neutral')
        return random.choice(cls().neutral)

    @classmethod
    def get_happy_sticker(cls):
        logger.debug('Возвращаем рандомный стикер из категории happy')
        return random.choice(cls().happy)


class User(BaseModel):
    id: Optional[int] = None
    tg_id: int
    mode: Optional[str] = Modes().all
    skill: Optional[str] = skills.Basic().short_name


class SubscriptionStatus(BaseModel):
    active: str = 'active'
    inactive: str = 'inactive'

