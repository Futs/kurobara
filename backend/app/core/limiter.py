try:
    import redis.asyncio as redis
    from fastapi_limiter import FastAPILimiter
    from fastapi_limiter.depends import RateLimiter
    RATE_LIMITING_AVAILABLE = True
except ImportError:
    RATE_LIMITING_AVAILABLE = False
    # Create dummy classes/functions for when Redis is not available
    class DummyRateLimiter:
        def __init__(self, times=0, seconds=0):
            pass
        
        def __call__(self):
            return lambda: None
    
    RateLimiter = DummyRateLimiter

from fastapi import Request, Response
import asyncio
from typing import Optional

from app.core.config import settings

# Redis client for rate limiting
redis_client: Optional[redis.Redis] = None if RATE_LIMITING_AVAILABLE else None


async def init_limiter():
    """Initialize the rate limiter with Redis."""
    if not RATE_LIMITING_AVAILABLE:
        print("Rate limiting is not available: Redis package not installed")
        return
        
    global redis_client
    try:
        redis_client = redis.from_url(
            settings.REDIS_URL, 
            encoding="utf-8", 
            decode_responses=True
        )
        await FastAPILimiter.init(redis_client)
        print("Rate limiting initialized successfully")
    except Exception as e:
        print(f"Failed to initialize rate limiter: {e}")


async def close_limiter():
    """Close Redis connection."""
    global redis_client
    if RATE_LIMITING_AVAILABLE and redis_client:
        await redis_client.close()


# Rate limit decorators for different endpoints
def default_rate_limit():
    """Default rate limit: 100 requests per minute."""
    if not RATE_LIMITING_AVAILABLE:
        return lambda: None
    return RateLimiter(times=100, seconds=60)


def auth_rate_limit():
    """Stricter rate limit for authentication: 5 requests per minute."""
    if not RATE_LIMITING_AVAILABLE:
        return lambda: None
    return RateLimiter(times=5, seconds=60)


def search_rate_limit():
    """Rate limit for search: 20 requests per minute."""
    if not RATE_LIMITING_AVAILABLE:
        return lambda: None
    return RateLimiter(times=20, seconds=60)
