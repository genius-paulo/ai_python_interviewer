import pytest
from src.db import db


@pytest.mark.asyncio
async def test_create_user(conftest_db):
    # Создаем пользователя
    await db.create_user(12345678)
    # Проверяем, что пользователь был создан
    user = await db.get_user(12345678)
    assert user is not None


@pytest.mark.asyncio
async def test_update_mode(conftest_db):
    # Обновляем режим пользователя
    await db.update_mode(12345678, 'new_mode')
    # Проверяем, что режим пользователя был обновлен
    user = await db.get_user(12345678)
    assert user.mode == 'new_mode'


@pytest.mark.asyncio
async def test_update_skill(conftest_db):
    # Обновляем навык пользователя
    await db.update_skill(12345678, 'new_skill')
    # Проверяем, что навык пользователя был обновлен
    user = await db.get_user(12345678)
    assert user.skill == 'new_skill'


@pytest.mark.asyncio
async def test_update_skill_rating(conftest_db):
    # Обновляем оценку по навыку пользователя
    await db.update_skill_rating(12345678, 'basic', 10)
    # Проверяем, что оценка по навыку пользователя была обновлена
    user = await db.get_user(12345678)
    assert user.basic == 10
