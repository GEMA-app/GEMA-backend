from fastapi import APIRouter, Depends, HTTPException, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine

from app.composition.container import get_db_engine, get_redis_client

router = APIRouter(tags=["salud"])


@router.get("/salud/activo", status_code=status.HTTP_200_OK, summary="Verificación de Liveness")
async def liveness() -> dict[str, str]:
    """Endpoint de liveness para verificar que el proceso de la aplicación está en ejecución."""
    return {"status": "ok"}


@router.get("/salud/listo", status_code=status.HTTP_200_OK, summary="Verificación de Readiness")
async def readiness(
    engine: AsyncEngine = Depends(get_db_engine),
    redis_client: Redis = Depends(get_redis_client),
) -> dict[str, str]:
    """Endpoint de readiness para verificar la base de datos y la caché Redis."""
    try:
        async with engine.connect():
            pass
        await redis_client.ping()
        return {"status": "ready"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unavailable: {e}",
        ) from e
