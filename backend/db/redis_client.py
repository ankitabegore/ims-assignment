import redis.asyncio as redis
from config import settings

class RedisClient:
    def __init__(self):
        self.client = None

    async def connect(self):
        self.client = redis.from_url(settings.REDIS_URL, decode_responses=True)

    async def close(self):
        if self.client:
            await self.client.aclose()

redis_client = RedisClient()
