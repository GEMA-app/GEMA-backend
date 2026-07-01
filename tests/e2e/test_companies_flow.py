"""Test E2E para el flujo de empresas (tenants)."""

import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.presentation.api.v1.endpoints.dependencies import rate_limit_by_email


@pytest.mark.asyncio
async def test_companies_crud_flow():
    """CRUD de empresas (tenants)."""
    # Mockear el rate limit
    app.dependency_overrides[rate_limit_by_email] = lambda: None

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            headers = {
                "Content-Type": "application/vnd.api+json",
                "Accept": "application/vnd.api+json",
            }

            # 1. Registrar empresa + usuario administrador inicial
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

            # Obtener ID de la empresa del usuario
            res_me = await client.get("/v1/auth/yo", headers=auth_headers)
            empresa_id = res_me.json()["data"]["attributes"]["empresa_id"]

            # 2. Obtener detalles de la propia empresa (GET /v1/empresas/{empresa_id})
            res = await client.get(f"/v1/empresas/{empresa_id}", headers=auth_headers)
            assert res.status_code == 200
            data = res.json()["data"]
            assert data["id"] == empresa_id
            assert data["attributes"]["nombre"] == f"Test Co {suffix}"

            # 3. Listar empresas (GET /v1/empresas)
            res = await client.get("/v1/empresas", headers=auth_headers)
            assert res.status_code == 200
            companies_list = res.json()["data"]
            assert len(companies_list) >= 1
            company_ids = [c["id"] for c in companies_list]
            assert empresa_id in company_ids

            # 4. Actualizar la propia empresa (PATCH /v1/empresas/{empresa_id})
            new_name = f"Updated Co {suffix}"
            res = await client.patch(f"/v1/empresas/{empresa_id}", json={
                "data": {"type": "companies", "id": empresa_id, "attributes": {
                    "nombre": new_name,
                    "version": data["attributes"]["version"],
                }},
            }, headers=auth_headers)
            assert res.status_code == 200
            assert res.json()["data"]["attributes"]["nombre"] == new_name

            # 5. Crear una nueva empresa (POST /v1/empresas)
            new_suffix = uuid.uuid4().hex[:8]
            res = await client.post("/v1/empresas", json={
                "data": {"type": "companies", "attributes": {
                    "nombre": f"Another Co {new_suffix}",
                    "slug": f"another-co-{new_suffix}",
                    "rif": f"J-{new_suffix}",
                    "email_contacto": f"contact_{new_suffix}@example.com",
                }},
            }, headers=auth_headers)
            assert res.status_code == 201
            created_co_id = res.json()["data"]["id"]

            # 6. Eliminar empresa ajena retorna 403 (tenant isolation)
            res = await client.delete(f"/v1/empresas/{created_co_id}", headers=auth_headers)
            assert res.status_code == 403, f"Esperado 403 por tenant isolation, obtuvo {res.status_code}"

    finally:
        app.dependency_overrides.clear()
