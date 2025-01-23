import pytest_asyncio
import pytest
from src.db.models import Users
from src.db.db import *


@pytest.mark.asyncio
async def test_create_user(db):
    # Создаем пользователя
    await create_user(12345678)
    # Проверяем, что пользователь был создан
    user = await get_user(12345678)
    assert user is not None


@pytest.mark.asyncio
async def test_update_mode(db):
    # Обновляем режим пользователя
    await update_mode(12345678, 'new_mode')
    # Проверяем, что режим пользователя был обновлен
    user = await get_user(12345678)
    assert user.mode == 'new_mode'


@pytest.mark.asyncio
async def test_update_skill(db):
    # Обновляем навык пользователя
    await update_skill(12345678, 'new_skill')
    # Проверяем, что навык пользователя был обновлен
    user = await get_user(12345678)
    assert user.skill == 'new_skill'


@pytest.mark.asyncio
async def test_update_skill_rating(db):
    # Обновляем оценку по навыку пользователя
    await update_skill_rating(12345678, 'basic', 10)
    # Проверяем, что оценка по навыку пользователя была обновлена
    user = await get_user(12345678)
    assert user.basic == 10
