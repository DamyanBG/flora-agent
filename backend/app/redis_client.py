import redis.asyncio as redis
from typing import Optional

from app.config import settings


class RedisClient:
    """Async Redis client wrapper."""
    
    def __init__(self):
        self._redis: Optional[redis.Redis] = None
    
    async def connect(self) -> None:
        """Connect to Redis."""
        self._redis = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
    
    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self._redis:
            await self._redis.close()
            self._redis = None
    
    @property
    def client(self) -> redis.Redis:
        """Get the Redis client instance."""
        if self._redis is None:
            raise RuntimeError("Redis client is not connected")
        return self._redis
    
    async def get(self, key: str) -> Optional[str]:
        """Get a value from Redis."""
        return await self.client.get(key)
    
    async def set(self, key: str, value: str, ex: Optional[int] = None) -> None:
        """Set a value in Redis with optional expiration in seconds."""
        await self.client.set(key, value, ex=ex)
    
    async def delete(self, key: str) -> None:
        """Delete a key from Redis."""
        await self.client.delete(key)
    
    async def exists(self, key: str) -> bool:
        """Check if a key exists in Redis."""
        return await self.client.exists(key) > 0
    
    async def setex(self, key: str, seconds: int, value: str) -> None:
        """Set a value with expiration time."""
        await self.client.setex(key, seconds, value)


# Global Redis client instance
redis_client = RedisClient()


async def init_redis() -> None:
    """Initialize Redis connection."""
    await redis_client.connect()


async def close_redis() -> None:
    """Close Redis connection."""
    await redis_client.disconnect()


async def get_redis() -> RedisClient:
    """Dependency to get Redis client."""
    return redis_client

