import random
import asyncio
import re
import io
from loguru import logger

from src.bot.bot_content import basics, skills
from src.config import settings
from src.db import db

import matplotlib.pyplot as plt
import numpy as np
import textwrap
import uuid
import os


async def get_skill_by_category(user: db.Users) -> skills.Skills:
    """Возвращает навык пользователя в зависимости от режима
    тренировки"""

    if user.mode == basics.Modes().all:
        skill = random.choice(skills.Skills.get_all_skills())
        logger.info(f'Пользователь тренирует все скиллы. Выбираем навык рандомно: {skill}')
        return skill()

    elif user.mode == basics.Modes().specific:
        skill = skills.Skills.get_skill_by_name(user.skill)
        logger.info(f'Пользователь тренирует конкретный скилл: {skill}')
        return skill

    elif user.mode == basics.Modes().worst:
        # Получаем названия скиллов из класса SkillsData
        all_skills_names = skills.Skills.get_all_skills()

        # Создаем словарь, где ключи - это названия атрибутов в классе SkillsScores,
        # а значения — это оценки навыков пользователя
        skills_dict = {skill().short_name: getattr(user, skill().short_name) for skill in all_skills_names}

        # Получаем навык с самой низкой оценкой
        skill = skills.Skills.get_skill_by_name(min(skills_dict, key=skills_dict.get))
        logger.info(f'Пользователь тренирует самые слабые скиллы: {skill.short_description}')
        return skill


def parse_score_from_ai_answer(answer: str) -> int:
    """Парсим оценку из ответа нейросети"""
    match = re.search(r'Оценка: (\d+/\d+)', answer)
    if match:
        score = int(match.group(1).split('/')[0])
    else:
        raise ValueError("Оценка не найдена в ответе нейросети")
    logger.info(f'Спарсили оценку из ответа нейросети: {score}')
    return score


def get_new_skill_rating(current_rating, new_score, alpha=settings.alpha_coefficient):
    """Пересчитываем оценку, используя метод экспоненциального сглаживания
    для обновления средней оценки"""
    new_score = alpha * new_score + (1 - alpha) * current_rating
    round_new_score = round(new_score, 1)
    logger.info(f'Пересчитываем оценку, используя метод экспоненциального сглаживания: {round_new_score}')
    return round_new_score


async def create_skill_map(user: db.Users) -> bytes:
    """Создаем диаграмму паука с оценкой навыков"""
    logger.info('Создаем диаграмму паука с оценкой навыков')

    # Получаем названия скиллов из класса SkillsData
    all_skills_names = skills.Skills.get_all_skills()
    # Создаем словарь, где ключи - это названия атрибутов в классе SkillsScores,
    # а значения — это названия навыков на русском
    skills_dict = {skill().short_name: skill().short_description for skill in all_skills_names}
    logger.debug(f'Скиллы при создании карты: {skills_dict=}')
    # Создаем список оценок для каждого навыка
    scores = [getattr(user, skill().short_name) for skill in all_skills_names]
    logger.debug(f'Оценки при создании карты: {scores=}')

    # Создаем массив углов для каждого навыка
    angles = np.linspace(0, 2*np.pi, len(skills_dict), endpoint=False).tolist()

    # Добавляем первый угол в конец, чтобы замкнуть диаграмму
    angles += angles[:1]
    scores += scores[:1]

    # Создаем фигуру и оси
    fig = plt.figure(tight_layout=True, figsize=(10, 10))
    ax = fig.add_subplot(111, polar=True)

    # Рисуем диаграмму паука
    ax.plot(angles, scores, 'o-', linewidth=2)
    ax.fill(angles, scores, alpha=0.25)

    # Устанавливаем метки для каждого навыка
    labels = [textwrap.fill(label, 10, break_long_words=False) for label in skills_dict.values()]
    angles_degrees = np.degrees(angles[:-1])
    ax.set_thetagrids(angles_degrees, labels)
    # Устанавливаем диапазон значений для оси Y
    ax.set_ylim(0, 10)
    # Увеличиваем размер шрифта и отступы для меток
    ax.tick_params(labelsize=15, pad=60)

    # Устанавливаем отступы для подграфиков
    plt.subplots_adjust(left=0.20, right=0.80, top=0.80, bottom=0.20)

    # Создаем объект BytesIO
    img_bytes = io.BytesIO()

    # Сохраняем картинку в объект BytesIO
    await asyncio.to_thread(plt.savefig, img_bytes, format='png')

    # Возвращаем массив байтов
    return img_bytes.getvalue()


def get_average_skill_score(user: db.Users) -> float:
    """Возвращает среднюю оценку навыков пользователя"""
    all_skills_names = skills.Skills.get_all_skills()
    scores = [getattr(user, skill().short_name) for skill in all_skills_names]
    average_score = sum(scores) / len(scores)
    # Округляем среднюю оценку
    average_score = round(average_score, 1)
    logger.info(f'Средняя оценка навыков пользователя: {average_score}')
    return average_score


def get_skill_map_name(user: db.Users, mode: str = 'file'):
    """Возвращает имя файла для сохранения диаграммы паука:
    — mode='file' возвращает имя файла с .png
    — mode='key' возвращает ключ для сохранения карты в кэше без .png"""
    if mode == 'file':
        return f'skill_map_{user.tg_id}.png'
    elif mode == 'key':
        return f'skill_map_{user.tg_id}'


def get_sticker_by_score(ai_answer_score: int) -> str:
    """Возвращает стикер в зависимости от оценки на ответ"""
    if 0 <= ai_answer_score < 4:
        # Возвращаем рандомный стикер из категории sad
        return basics.Stickers().get_sad_sticker()
    elif 4 <= ai_answer_score < 7:
        # Возвращаем рандомный стикер из категории neutral
        return basics.Stickers().get_neutral_sticker()
    elif 7 <= ai_answer_score <= 10:
        # Возвращаем рандомный стикер из категории happy
        return basics.Stickers().get_happy_sticker()
    else:
        # Возвращаем ошибку
        raise ValueError('Неверная оценка')


if __name__ == '__main__':
    logger.info(get_new_skill_rating(8, 9))
    for i in range(11):
        logger.info(f'Оценка: {i}. Стикер: {get_sticker_by_score(i)}')
