"""Test E2E para preferencias de usuario."""

import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.presentation.api.v1.endpoints.dependencies import rate_limit_by_email


@pytest.mark.asyncio
async def test_preferences_crud_flow():
    """CRUD de preferencias del usuario autenticado."""
    app.dependency_overrides[rate_limit_by_email] = lambda: None

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            headers = {
                "Content-Type": "application/vnd.api+json",
                "Accept": "application/vnd.api+json",
            }

            # Registrar empresa + usuario
            suffix = uuid.uuid4().hex[:8]
            res = await client.post("/v1/auth/registrar", json={
                "data": {"type": "users", "attributes": {
                    "email": f"admin_{suffix}@example.com",
                    "password": "Password123!",
                    "nombre": "Admin Test",
                    "company_name": f"Test Co {suffix}",
                    "telefono": "+1111111111",
                }},
            }, headers=headers)
            assert res.status_code == 201
            token = res.json()["data"]["attributes"]["access_token"]
            auth_headers = {**headers, "Authorization": f"Bearer {token}"}

            res_me = await client.get("/v1/auth/yo", headers=auth_headers)
            empresa_id = res_me.json()["data"]["attributes"]["empresa_id"]

            # GET preferencias (se crean automáticamente con el usuario)
            res = await client.get(f"/v1/empresas/{empresa_id}/yo/preferencias", headers=auth_headers)
            assert res.status_code == 200
            data = res.json()["data"]
            assert "attributes" in data
            assert "tema" in data["attributes"]

            # PATCH preferencias
            res = await client.patch(f"/v1/empresas/{empresa_id}/yo/preferencias", json={
                "data": {"type": "preferences", "id": data["id"], "attributes": {
                    "tema": "oscuro",
                    "version": data["attributes"]["version"],
                }},
            }, headers=auth_headers)
            assert res.status_code == 200, f"PATCH failed: {res.text}"
            assert res.json()["data"]["attributes"]["tema"] == "oscuro"
    finally:
        app.dependency_overrides.clear()
