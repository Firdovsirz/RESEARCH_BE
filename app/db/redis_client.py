import os
import redis.asyncio as redis

redis_client = None

async def get_redis():
    global redis_client
    if not redis_client:
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        redis_client = redis.from_url(
            redis_url,
            decode_responses=True
        )
    return redis_client