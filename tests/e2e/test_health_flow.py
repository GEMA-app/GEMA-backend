"""Test E2E para endpoints de salud (liveness + readiness)."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.presentation.api.v1.endpoints.dependencies import rate_limit_by_email


@pytest.mark.asyncio
async def test_health_endpoints():
    """Verificar que liveness y readiness responden correctamente."""
    app.dependency_overrides[rate_limit_by_email] = lambda: None

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Liveness - no requiere headers especiales
            res = await client.get("/salud/activo")
            assert res.status_code == 200
            assert res.json() == {"status": "ok"}

            # Readiness - verifica DB + Redis
            res = await client.get("/salud/listo")
            assert res.status_code == 200
            assert res.json() == {"status": "ready"}
    finally:
        app.dependency_overrides.clear()
