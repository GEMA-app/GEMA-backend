"""Test E2E para verificar el CRUD y aislamiento multi-tenant de Ejecuciones de Plan (PlanExecution)."""

import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.presentation.api.v1.endpoints.dependencies import rate_limit_by_email


@pytest.mark.asyncio
async def test_plan_executions_crud_and_isolation_flow() -> None:
    """Test E2E para verificar CRUD e isolation multi-tenant de PlanExecution."""
    app.dependency_overrides[rate_limit_by_email] = lambda: None

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            headers = {
                "Content-Type": "application/vnd.api+json",
                "Accept": "application/vnd.api+json",
            }

            # =====================================================================
            # CONFIGURACIÓN: Registrar Compañía A y Compañía B
            # =====================================================================
            id_a = uuid.uuid4().hex[:8]
            email_a = f"admin_a_{id_a}@example.com"
            password = "Password123!"
            reg_a = await client.post("/v1/auth/registrar", json={
                "data": {"type": "users", "attributes": {
                    "email": email_a, "password": password, "nombre": "Admin A",
                    "company_name": f"Company A {id_a}", "telefono": "+1111111111",
                }}
            }, headers=headers)
            assert reg_a.status_code == 201
            token_a = reg_a.json()["data"]["attributes"]["access_token"]
            ah_a = {**headers, "Authorization": f"Bearer {token_a}"}
            me_a = await client.get("/v1/auth/yo", headers=ah_a)
            eid_a = me_a.json()["data"]["attributes"]["empresa_id"]

            id_b = uuid.uuid4().hex[:8]
            email_b = f"admin_b_{id_b}@example.com"
            reg_b = await client.post("/v1/auth/registrar", json={
                "data": {"type": "users", "attributes": {
                    "email": email_b, "password": password, "nombre": "Admin B",
                    "company_name": f"Company B {id_b}", "telefono": "+2222222222",
                }}
            }, headers=headers)
            assert reg_b.status_code == 201
            token_b = reg_b.json()["data"]["attributes"]["access_token"]
            ah_b = {**headers, "Authorization": f"Bearer {token_b}"}
            # =====================================================================
            # PREREQUISITOS: artículo catálogo + activo + plan + orden trabajo
            # =====================================================================
            # Artículo de catálogo
            res = await client.post(
                f"/v1/empresas/{eid_a}/catalogo/articulos",
                json={"data": {"type": "catalog-articles", "attributes": {
                    "name": "Motor Eléctrico 50HP",
                }}},
                headers=ah_a,
            )
            assert res.status_code == 201
            articulo_id = res.json()["data"]["id"]

            # Activo
            res = await client.post(f"/v1/empresas/{eid_a}/activos", json={
                "data": {"type": "assets", "attributes": {
                    "articulo_id": articulo_id,
                    "serial_interno": f"SN-{id_a}",
                    "codigo_activo": f"ACT-{id_a}",
                    "estado": "operativo",
                }}
            }, headers=ah_a)
            assert res.status_code == 201
            activo_id = res.json()["data"]["id"]

            # Plan de mantenimiento
            futuro = "2026-12-31"
            res = await client.post(f"/v1/empresas/{eid_a}/planes-mantenimiento", json={
                "data": {"type": "maintenance-plans", "attributes": {
                    "activo_id": activo_id, "nombre": "Plan Test Ejecuciones",
                    "tipo": "preventivo", "intervalo_dias": 90,
                    "proxima_ejecucion": futuro,
                }}
            }, headers=ah_a)
            assert res.status_code == 201
            plan_id = res.json()["data"]["id"]

            # Orden de trabajo
            res = await client.post(f"/v1/empresas/{eid_a}/ordenes-trabajo", json={
                "data": {"type": "work_orders", "attributes": {
                    "activo_id": activo_id, "tipo": "correctivo",
                }}
            }, headers=ah_a)
            assert res.status_code == 201, f"Crear OT: {res.text}"
            wo_id = res.json()["data"]["id"]

            # =====================================================================
            # Paso 1: CREAR ejecución de plan (POST)
            # =====================================================================
            exec_date = "2026-06-15T10:00:00Z"
            create_payload = {
                "data": {
                    "type": "planExecution",
                    "attributes": {
                        "plan_id": plan_id,
                        "work_order_id": wo_id,
                        "execution_date": exec_date,
                        "observations": "Ejecución de prueba exitosa.",
                    },
                }
            }
            res_create = await client.post(
                f"/v1/empresas/{eid_a}/planes-mantenimiento/{plan_id}/ejecuciones",
                json=create_payload, headers=ah_a,
            )
            assert res_create.status_code == 201, f"Crear ejecución: {res_create.text}"
            data_c = res_create.json()["data"]
            exec_id = data_c["id"]
            attrs = data_c["attributes"]
            assert attrs["plan_id"] == plan_id
            assert attrs["work_order_id"] == wo_id
            assert attrs["observations"] == "Ejecución de prueba exitosa."
            assert attrs["empresa_id"] == eid_a

            # =====================================================================
            # Paso 2: OBTENER ejecución por ID (GET)
            # =====================================================================
            res_get = await client.get(
                f"/v1/empresas/{eid_a}/planes-mantenimiento/{plan_id}/ejecuciones/{exec_id}",
                headers=ah_a,
            )
            assert res_get.status_code == 200
            assert res_get.json()["data"]["id"] == exec_id

            # =====================================================================
            # Paso 3: LISTAR ejecuciones
            # =====================================================================
            res_list = await client.get(
                f"/v1/empresas/{eid_a}/planes-mantenimiento/{plan_id}/ejecuciones",
                headers=ah_a,
            )
            assert res_list.status_code == 200
            ids = [i["id"] for i in res_list.json()["data"]]
            assert exec_id in ids

            # =====================================================================
            # Paso 4: Validar observaciones vacías → 422
            # =====================================================================
            res_empty = await client.post(
                f"/v1/empresas/{eid_a}/planes-mantenimiento/{plan_id}/ejecuciones",
                json={
                    "data": {
                        "type": "planExecution",
                        "attributes": {
                            "plan_id": plan_id,
                            "work_order_id": wo_id,
                            "execution_date": exec_date,
                            "observations": "   ",
                        },
                    }
                },
                headers=ah_a,
            )
            assert res_empty.status_code == 422
            assert "ERR_PLAN_EXECUTION_OBSERVATIONS_EMPTY" in res_empty.text

            # =====================================================================
            # Paso 5: Aislamiento MULTI-TENANT
            # =====================================================================
            # Compañía B no puede obtener ejecución de Compañía A
            res_get_b = await client.get(
                f"/v1/empresas/{eid_a}/planes-mantenimiento/{plan_id}/ejecuciones/{exec_id}",
                headers=ah_b,
            )
            assert res_get_b.status_code == 403

            # Compañía B no puede listar ejecuciones de Compañía A
            res_list_b = await client.get(
                f"/v1/empresas/{eid_a}/planes-mantenimiento/{plan_id}/ejecuciones",
                headers=ah_b,
            )
            assert res_list_b.status_code == 403

            # Compañía B no puede crear ejecución en Compañía A
            res_create_b = await client.post(
                f"/v1/empresas/{eid_a}/planes-mantenimiento/{plan_id}/ejecuciones",
                json=create_payload, headers=ah_b,
            )
            assert res_create_b.status_code == 403

            # =====================================================================
            # Paso 6: Obtener ejecución inexistente → 404
            # =====================================================================
            fake_id = "00000000-0000-0000-0000-000000000000"
            res_not_found = await client.get(
                f"/v1/empresas/{eid_a}/planes-mantenimiento/{plan_id}/ejecuciones/{fake_id}",
                headers=ah_a,
            )
            assert res_not_found.status_code == 404
            assert "ERR_PLAN_EXECUTION_NOT_FOUND" in res_not_found.text

    finally:
        app.dependency_overrides.clear()
