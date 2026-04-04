import os
import redis.asyncio as redis
from typing import Optional

class RedisClient:
    def __init__(self):
        self.client: Optional[redis.Redis] = None

    async def connect(self):
        if not self.client:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
            self.client = redis.from_url(
                redis_url,
                decode_responses=True
            )
        return self.client

    async def disconnect(self):
        if self.client:
            await self.client.close()
            self.client = None

    def __call__(self) -> redis.Redis:
        if not self.client:
            raise RuntimeError("RedisClient is not connected. Use connect() first.")
        return self.client

redis_manager = RedisClient()

async def get_redis() -> redis.Redis:
    return await redis_manager.connect()
