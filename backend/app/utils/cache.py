import json
from typing import Any, Optional, Callable
from functools import wraps

from app.redis_client import redis_client


# Cache key prefixes
CACHE_PREFIX_FLOWERS = "flowers:"
CACHE_PREFIX_TOKEN_BLACKLIST = "token_blacklist:"

# Default TTL values (in seconds)
DEFAULT_CACHE_TTL = 300  # 5 minutes


async def get_cached(key: str) -> Optional[Any]:
    """Get a value from cache and deserialize it."""
    value = await redis_client.get(key)
    if value:
        return json.loads(value)
    return None


async def set_cached(key: str, value: Any, ttl: int = DEFAULT_CACHE_TTL) -> None:
    """Serialize and set a value in cache with TTL."""
    serialized = json.dumps(value, default=str)
    await redis_client.set(key, serialized, ex=ttl)


async def delete_cached(key: str) -> None:
    """Delete a cached value."""
    await redis_client.delete(key)


async def invalidate_pattern(pattern: str) -> None:
    """Invalidate all keys matching a pattern."""
    client = redis_client.client
    async for key in client.scan_iter(match=pattern):
        await client.delete(key)


# Token blacklist functions
async def blacklist_token(token: str, ttl: int) -> None:
    """Add a token to the blacklist with expiration."""
    key = f"{CACHE_PREFIX_TOKEN_BLACKLIST}{token}"
    await redis_client.setex(key, ttl, "blacklisted")


async def is_token_blacklisted(token: str) -> bool:
    """Check if a token is blacklisted."""
    key = f"{CACHE_PREFIX_TOKEN_BLACKLIST}{token}"
    return await redis_client.exists(key)


# Flower cache functions
def get_flowers_list_key(skip: int = 0, limit: int = 100) -> str:
    """Generate cache key for flowers list."""
    return f"{CACHE_PREFIX_FLOWERS}list:{skip}:{limit}"


async def invalidate_flowers_cache() -> None:
    """Invalidate all flower-related cache."""
    await invalidate_pattern(f"{CACHE_PREFIX_FLOWERS}*")


