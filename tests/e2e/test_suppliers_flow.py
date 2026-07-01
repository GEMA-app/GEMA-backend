"""Test E2E para CRUD de proveedores con aislamiento multi-tenant."""

import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.presentation.api.v1.endpoints.dependencies import rate_limit_by_email


@pytest.mark.asyncio
async def test_suppliers_crud_and_isolation_flow():
    """CRUD de proveedores + verificación de aislamiento entre tenants."""
    app.dependency_overrides[rate_limit_by_email] = lambda: None

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            headers = {
                "Content-Type": "application/vnd.api+json",
                "Accept": "application/vnd.api+json",
            }

            # Registrar Tenant A
            id_a = uuid.uuid4().hex[:8]
            res = await client.post("/v1/auth/registrar", json={
                "data": {"type": "users", "attributes": {
                    "email": f"admin_a_{id_a}@example.com",
                    "password": "Password123!",
                    "nombre": "Admin A",
                    "company_name": f"Company A {id_a}",
                    "telefono": "+1111111111",
                }},
            }, headers=headers)
            assert res.status_code == 201
            token_a = res.json()["data"]["attributes"]["access_token"]
            res_me = await client.get("/v1/auth/yo", headers={**headers, "Authorization": f"Bearer {token_a}"})
            empresa_a = res_me.json()["data"]["attributes"]["empresa_id"]
            auth_a = {**headers, "Authorization": f"Bearer {token_a}"}

            # Registrar Tenant B
            id_b = uuid.uuid4().hex[:8]
            res = await client.post("/v1/auth/registrar", json={
                "data": {"type": "users", "attributes": {
                    "email": f"admin_b_{id_b}@example.com",
                    "password": "Password123!",
                    "nombre": "Admin B",
                    "company_name": f"Company B {id_b}",
                    "telefono": "+2222222222",
                }},
            }, headers=headers)
            assert res.status_code == 201
            token_b = res.json()["data"]["attributes"]["access_token"]
            auth_b = {**headers, "Authorization": f"Bearer {token_b}"}

            # CREATE - Tenant A
            res = await client.post(f"/v1/empresas/{empresa_a}/proveedores", json={
                "data": {"type": "suppliers", "attributes": {
                    "name": "Proveedor A",
                    "rif": "J-11111111-1",
                    "phone": "+584141111111",
                    "email": "prova@test.com",
                    "contact": "Juan A",
                }},
            }, headers=auth_a)
            assert res.status_code == 201, f"Create A falló: {res.text}"
            sup_a_id = res.json()["data"]["id"]
            assert res.json()["data"]["attributes"]["name"] == "Proveedor A"

            # CREATE - Tenant B (mismo RIF debe ser válido en otro tenant)
            res = await client.post(f"/v1/empresas/{empresa_a}/proveedores", json={
                "data": {"type": "suppliers", "attributes": {
                    "name": "Proveedor B",
                    "rif": "J-11111111-1",
                    "phone": "+584142222222",
                    "email": "provb@test.com",
                    "contact": "Maria B",
                }},
            }, headers=auth_b)
            # B no puede crear en empresa A (tenant isolation)
            assert res.status_code == 403, f"Tenant isolation A->B falló: {res.text}"

            # CREATE - Tenant B en su propia empresa
            res_me_b = await client.get("/v1/auth/yo", headers=auth_b)
            empresa_b = res_me_b.json()["data"]["attributes"]["empresa_id"]

            res = await client.post(f"/v1/empresas/{empresa_b}/proveedores", json={
                "data": {"type": "suppliers", "attributes": {
                    "name": "Proveedor B",
                    "rif": "J-22222222-2",
                    "phone": "+584142222222",
                    "email": "provb@test.com",
                    "contact": "Maria B",
                }},
            }, headers=auth_b)
            assert res.status_code == 201, f"Create B falló: {res.text}"
            _sup_b_id = res.json()["data"]["id"]

            # LIST - Tenant A (solo debe ver su proveedor)
            res = await client.get(f"/v1/empresas/{empresa_a}/proveedores", headers=auth_a)
            assert res.status_code == 200
            data_a = res.json()["data"]
            assert len(data_a) == 1
            assert data_a[0]["id"] == sup_a_id

            # GET by ID
            res = await client.get(f"/v1/empresas/{empresa_a}/proveedores/{sup_a_id}", headers=auth_a)
            assert res.status_code == 200
            assert res.json()["data"]["attributes"]["name"] == "Proveedor A"

            # UPDATE
            res = await client.patch(f"/v1/empresas/{empresa_a}/proveedores/{sup_a_id}", json={
                "data": {"type": "suppliers", "attributes": {
                    "name": "Proveedor A Actualizado",
                    "rif": "J-11111111-1",
                    "version": 1,
                }},
            }, headers=auth_a)
            assert res.status_code == 200
            assert res.json()["data"]["attributes"]["name"] == "Proveedor A Actualizado"

            # DELETE
            res = await client.delete(f"/v1/empresas/{empresa_a}/proveedores/{sup_a_id}", headers=auth_a)
            assert res.status_code == 204

            # Verify deleted
            res = await client.get(f"/v1/empresas/{empresa_a}/proveedores", headers=auth_a)
            assert len(res.json()["data"]) == 0
    finally:
        app.dependency_overrides.clear()
