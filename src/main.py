import asyncio
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from src.config import settings
from src.bot.handlers import register_handlers
from src.db import db, models
from loguru import logger
# TODO: Нужно реализовать нормальное логгирование и мониторинг показателей,
#  сейчас надеюсь на чудо


class CustomDispatcher(Dispatcher):
    async def _process_polling_updates(self, updates, fast):
        try:
            return await super()._process_polling_updates(updates, fast)
        except Exception as e:
            logger.exception("Ошибка при обработке update:")
            # Отправляем сообщение об ошибке администратору
            for update in updates:
                if update.message:
                    text = (f"У пользователя {update.message.from_user.username} "
                            f"(id: {update.message.from_user.id}) произошла ошибка: {e}")
                    logger.info(f'Отправляем сообщение об ошибке администратору: {text}')
                    await self.bot.send_message(settings.admin_chat_id,
                                                text)


# Инициализируем бота
bot = Bot(token=settings.tg_token)
# Инициализируем объект памяти для хранения состояний
storage = MemoryStorage()
logger.info(f'Инициализировали объект памяти для состояний: {bot}')
# Инициализируем диспетчер
dp = CustomDispatcher(bot, storage=storage)
logger.info(f'Инициализировали диспетчер: {bot}')



async def main():
    try:
        # Инициализация БД
        logger.info(f'Подключились к базе данных: {db.db}')
        # Создали в БД таблицы
        await db.create_tables(models.Users())
        logger.info(f'Таблицы созданы')
        logger.info(f'Бот инициализирован: {bot}')
        # Асинхронная регистрация обработчиков
        await register_handlers(dp)
        logger.info(f'Хэндлеры инициализированы')

        # Запускаем бота
        await dp.start_polling()
    finally:
        # Закрываем сессию и другие ресурсы асинхронно
        session = await bot.get_session()
        await session.close()
        await storage.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())  # Запускаем основную асинхронную функцию
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот остановлен")
