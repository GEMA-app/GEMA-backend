import redis.asyncio as aioredis

from app.infrastructure.config.settings import settings

# Cliente global asíncrono de Redis
redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)  # type: ignore[no-untyped-call]


async def get_redis() -> aioredis.Redis:
    """Devuelve la instancia global del cliente asíncrono de Redis."""
    return redis_client  # type: ignore[no-any-return]
