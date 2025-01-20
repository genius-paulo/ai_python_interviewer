from src.config import settings
from redis.asyncio import Redis
import asyncio


class CacheClient:
    def __init__(self, host: str, port: int, db: str):
        self.redis = Redis(host=host,
                           port=port,
                           db=db)

    async def get(self, key: str):
        return await self.redis.get(key)

    async def set(self, key: str, value: str, expire: int = None):
        await self.redis.set(key, value, ex=expire)

    async def exists(self, key: str):
        return await self.redis.exists(key)

    async def delete(self, key: str):
        await self.redis.delete(key)

    async def close(self):
        await self.redis.close()


# Использование в приложении
cache = CacheClient(host=settings.redis_host,
                    port=settings.redis_port,
                    db=settings.redis_count_db)


async def main():

    # Устанавливаем значение ключа
    await cache.set("key", "value")

    # Получаем значение ключа
    value = await cache.get("key")
    print(f"The value of 'key' is: {value}")


if __name__ == '__main__':
    # Запускаем асинхронный код
    asyncio.run(main())
