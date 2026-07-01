"""Test E2E para CRUD de roles + asignación/revocación con aislamiento multi-tenant."""

import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.presentation.api.v1.endpoints.dependencies import rate_limit_by_email


@pytest.mark.asyncio
async def test_roles_crud_and_assign_flow():
    """CRUD de roles + assign/revoke + verificación de aislamiento entre tenants."""
    app.dependency_overrides[rate_limit_by_email] = lambda: None

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            headers = {
                "Content-Type": "application/vnd.api+json",
                "Accept": "application/vnd.api+json",
            }

            # Registrar Tenant A
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
            mi_user_id = res_me.json()["data"]["id"]

            # CREATE rol
            res = await client.post(f"/v1/empresas/{empresa_id}/roles", json={
                "data": {"type": "roles", "attributes": {
                    "nombre": "Supervisor",
                    "descripcion": "Rol de supervisión",
                    "permisos": [
                        {"module": "activos", "can_view": True, "can_create": False, "can_edit": False, "can_delete": False},
                    ],
                }},
            }, headers=auth)
            assert res.status_code == 201, f"Create rol falló: {res.text}"
            rol_id = res.json()["data"]["id"]
            assert res.json()["data"]["attributes"]["nombre"] == "Supervisor"
            version = res.json()["data"]["attributes"]["version"]

            # LIST roles
            res = await client.get(f"/v1/empresas/{empresa_id}/roles", headers=auth)
            assert res.status_code == 200
            rol_ids = [r["id"] for r in res.json()["data"]]
            assert rol_id in rol_ids

            # GET by ID
            res = await client.get(f"/v1/empresas/{empresa_id}/roles/{rol_id}", headers=auth)
            assert res.status_code == 200
            assert res.json()["data"]["attributes"]["nombre"] == "Supervisor"

            # UPDATE rol
            res = await client.patch(f"/v1/empresas/{empresa_id}/roles/{rol_id}", json={
                "data": {"type": "roles", "attributes": {
                    "nombre": "Supervisor Avanzado",
                    "version": version,
                }},
            }, headers=auth)
            assert res.status_code == 200
            assert res.json()["data"]["attributes"]["nombre"] == "Supervisor Avanzado"

            # ASSIGN rol al mismo usuario administrador
            res = await client.post(f"/v1/empresas/{empresa_id}/roles/{rol_id}/asignar", json={
                "data": {"type": "roles", "attributes": {
                    "usuario_id": mi_user_id,
                }},
            }, headers=auth)
            assert res.status_code == 204, f"Assign rol falló: {res.text}"

            # REVOKE rol
            res = await client.delete(
                f"/v1/empresas/{empresa_id}/roles/{rol_id}/revocar?usuario_id={mi_user_id}",
                headers=auth,
            )
            assert res.status_code == 204, f"Revoke rol falló: {res.text}"

            # DELETE rol
            res = await client.delete(f"/v1/empresas/{empresa_id}/roles/{rol_id}", headers=auth)
            assert res.status_code == 204

            # Verify deleted
            res = await client.get(f"/v1/empresas/{empresa_id}/roles", headers=auth)
            assert rol_id not in [r["id"] for r in res.json()["data"]]

            # TENANT ISOLATION: otro tenant no puede acceder
            suffix2 = uuid.uuid4().hex[:8]
            res = await client.post("/v1/auth/registrar", json={
                "data": {"type": "users", "attributes": {
                    "email": f"other_{suffix2}@example.com",
                    "password": "Password123!",
                    "nombre": "Other",
                    "company_name": f"Other Co {suffix2}",
                    "telefono": "+1222222222",
                }},
            }, headers=headers)
            assert res.status_code == 201
            token_b = res.json()["data"]["attributes"]["access_token"]
            auth_b = {**headers, "Authorization": f"Bearer {token_b}"}
            res_me_b = await client.get("/v1/auth/yo", headers=auth_b)
            empresa_b = res_me_b.json()["data"]["attributes"]["empresa_id"]

            res = await client.get(f"/v1/empresas/{empresa_b}/roles", headers=auth_b)
            assert res.status_code == 200
            # B no ve roles de A
            assert len(res.json()["data"]) == 1  # solo el rol Administrador creado al registrar

    finally:
        app.dependency_overrides.clear()
