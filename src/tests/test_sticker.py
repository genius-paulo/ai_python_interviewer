import random
import pytest
from aiogram import Bot, Dispatcher
from src.config import settings

# Предположим, что класс Stickers находится в модуле stickers
from src.bot.bot_content.basics import Stickers

# Предположим, что ваш чат ID находится в переменной CHAT_ID

bot = Bot(token=settings.tg_token)
dp = Dispatcher(bot)


@pytest.mark.asyncio
@pytest.mark.parametrize("stickers_list",
                         [Stickers().sad,
                          Stickers().neutral,
                          Stickers().happy])
async def test_send_stickers(stickers_list):
    for _ in range(10):
        sticker = random.choice(stickers_list)  # Получаем случайный стикер из списка
        result = await bot.send_sticker(chat_id=settings.admin_chat_id, sticker=sticker)
        assert result is not None  # Проверяем, что стикер был успешно отправлен
