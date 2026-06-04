from fastapi import APIRouter, HTTPException, status

from app.infrastructure.cache.redis import redis_client
from app.infrastructure.db.session import engine

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live", status_code=status.HTTP_200_OK, summary="Verificación de Liveness")
async def liveness() -> dict[str, str]:
    """Endpoint de liveness para verificar que el proceso de la aplicación está en ejecución."""
    return {"status": "ok"}


@router.get("/ready", status_code=status.HTTP_200_OK, summary="Verificación de Readiness")
async def readiness() -> dict[str, str]:
    """Endpoint de readiness para verificar la conectividad con la base de datos PostgreSQL y la caché Redis."""
    try:
        async with engine.connect():
            pass
        await redis_client.execute_command("PING")
        return {"status": "ready"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Service unavailable: {e}"
        )
