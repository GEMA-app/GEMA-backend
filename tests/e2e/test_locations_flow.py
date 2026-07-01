"""Test E2E para CRUD de ubicaciones jerárquicas + árbol + hijos."""

import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.presentation.api.v1.endpoints.dependencies import rate_limit_by_email


@pytest.mark.asyncio
async def test_locations_crud_and_tree_flow():
    """CRUD de ubicaciones + árbol jerárquico + consulta de hijos."""
    app.dependency_overrides[rate_limit_by_email] = lambda: None

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            headers = {
                "Content-Type": "application/vnd.api+json",
                "Accept": "application/vnd.api+json",
            }

            # Registrar tenant
            suffix = uuid.uuid4().hex[:8]
            res = await client.post("/v1/auth/registrar", json={
                "data": {"type": "users", "attributes": {
                    "email": f"admin_{suffix}@example.com",
                    "password": "Password123!",
                    "nombre": "Admin",
                    "company_name": f"Co {suffix}",
                    "telefono": "+1111111111",
                }},
            }, headers=headers)
            assert res.status_code == 201
            token = res.json()["data"]["attributes"]["access_token"]
            auth = {**headers, "Authorization": f"Bearer {token}"}
            res_me = await client.get("/v1/auth/yo", headers=auth)
            empresa_id = res_me.json()["data"]["attributes"]["empresa_id"]

            # CREATE ubicación raíz (sede)
            res = await client.post(f"/v1/empresas/{empresa_id}/ubicaciones", json={
                "data": {"type": "locations", "attributes": {
                    "nombre": "Sede Principal",
                    "tipo": "sede",
                    "descripcion": "Oficina central",
                }},
            }, headers=auth)
            assert res.status_code == 201, f"Create sede falló: {res.text}"
            sede_id = res.json()["data"]["id"]
            version = res.json()["data"]["attributes"]["version"]

            # CREATE ubicación hija (planta)
            res = await client.post(f"/v1/empresas/{empresa_id}/ubicaciones", json={
                "data": {"type": "locations", "attributes": {
                    "nombre": "Planta 1",
                    "tipo": "planta",
                    "parent_id": sede_id,
                    "descripcion": "Planta de producción",
                }},
            }, headers=auth)
            assert res.status_code == 201, f"Create planta falló: {res.text}"
            planta_id = res.json()["data"]["id"]

            # GET tree
            res = await client.get(f"/v1/empresas/{empresa_id}/ubicaciones", headers=auth)
            assert res.status_code == 200
            tree = res.json()["data"]
            assert len(tree) == 1
            assert tree[0]["id"] == sede_id
            assert len(tree[0]["attributes"]["children"]) == 1
            assert tree[0]["attributes"]["children"][0]["id"] == planta_id

            # GET by ID
            res = await client.get(f"/v1/empresas/{empresa_id}/ubicaciones/{sede_id}", headers=auth)
            assert res.status_code == 200
            assert res.json()["data"]["attributes"]["nombre"] == "Sede Principal"

            # GET children
            res = await client.get(f"/v1/empresas/{empresa_id}/ubicaciones/{sede_id}/hijos", headers=auth)
            assert res.status_code == 200
            hijos = res.json()["data"]
            assert len(hijos) == 1
            assert hijos[0]["id"] == planta_id

            # UPDATE ubicación
            res = await client.patch(f"/v1/empresas/{empresa_id}/ubicaciones/{sede_id}", json={
                "data": {"type": "locations", "attributes": {
                    "nombre": "Sede Principal Actualizada",
                    "version": version,
                }},
            }, headers=auth)
            assert res.status_code == 200
            assert res.json()["data"]["attributes"]["nombre"] == "Sede Principal Actualizada"

            # DELETE ubicación hija
            res = await client.delete(f"/v1/empresas/{empresa_id}/ubicaciones/{planta_id}", headers=auth)
            assert res.status_code == 204

            # Verificar que ya no está en el árbol
            res = await client.get(f"/v1/empresas/{empresa_id}/ubicaciones", headers=auth)
            assert len(res.json()["data"][0]["attributes"]["children"]) == 0

            # DELETE ubicación raíz
            res = await client.delete(f"/v1/empresas/{empresa_id}/ubicaciones/{sede_id}", headers=auth)
            assert res.status_code == 204

            # Verificar árbol vacío
            res = await client.get(f"/v1/empresas/{empresa_id}/ubicaciones", headers=auth)
            assert len(res.json()["data"]) == 0

    finally:
        app.dependency_overrides.clear()
