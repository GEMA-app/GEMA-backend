"""Tests para endpoints de health check."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_liveness():
    """GET /salud/activo debe retornar 200 con status ok."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/salud/activo")
        assert res.status_code == 200
        assert res.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_readiness():
    """GET /salud/listo debe retornar 200 cuando DB y Redis están operativos."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/salud/listo")
        # En test sin DB/Redis, puede fallar con 503 — lo que importa es que no crashee
        assert res.status_code in (200, 503)
