import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.presentation.api.v1.endpoints.dependencies import rate_limit_by_email


@pytest.mark.asyncio
async def test_interventions_crud_and_isolation_flow():
    """Test E2E para CRUD y aislamiento multi-tenant de intervenciones técnicas."""
    app.dependency_overrides[rate_limit_by_email] = lambda: None

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            headers = {
                "Content-Type": "application/vnd.api+json",
                "Accept": "application/vnd.api+json",
            }

            # =================================================================
            # CONFIG: Registrar Compañía A
            # =================================================================
            id_a = uuid.uuid4().hex[:8]
            email_a = f"admin_a_{id_a}@example.com"
            company_a_name = f"Company A {id_a}"
            password = "Password123!"

            reg_a = {
                "data": {
                    "type": "users",
                    "attributes": {
                        "email": email_a,
                        "password": password,
                        "nombre": "Admin A",
                        "company_name": company_a_name,
                        "telefono": "+1111111111",
                    },
                }
            }
            res = await client.post("/v1/auth/registrar", json=reg_a, headers=headers)
            assert res.status_code == 201, f"Registro A falló: {res.text}"
            tokens = res.json()["data"]["attributes"]
            access_token = tokens["access_token"]
            auth_headers = {**headers, "Authorization": f"Bearer {access_token}"}

            res_me = await client.get("/v1/auth/yo", headers=auth_headers)
            me = res_me.json()["data"]
            empresa_id = me["attributes"]["empresa_id"]
            usuario_id = me["id"]

            # =================================================================
            # SEED: artículo categoría → artículo catálogo → activo → OT
            # =================================================================
            cat = await client.post(
                f"/v1/empresas/{empresa_id}/catalogo/categorias",
                json={"data": {"type": "article_categories", "attributes": {"name": "Test Cat"}}},
                headers=auth_headers,
            )
            assert cat.status_code == 201
            category_id = cat.json()["data"]["id"]

            art = await client.post(
                f"/v1/empresas/{empresa_id}/catalogo/articulos",
                json={"data": {"type": "catalog-articles", "attributes": {"category_id": category_id, "name": "Test Art"}}},
                headers=auth_headers,
            )
            assert art.status_code == 201
            articulo_id = art.json()["data"]["id"]

            ast = await client.post(
                f"/v1/empresas/{empresa_id}/activos",
                json={"data": {"type": "assets", "attributes": {"articulo_id": articulo_id, "serial_interno": f"SN-{id_a}", "codigo_activo": f"ACT-{id_a}", "estado": "operativo"}}},
                headers=auth_headers,
            )
            assert ast.status_code == 201
            activo_id = ast.json()["data"]["id"]

            wo = await client.post(
                f"/v1/empresas/{empresa_id}/ordenes-trabajo",
                json={"data": {"type": "work_orders", "attributes": {"activo_id": activo_id, "tipo": "correctivo", "descripcion_trabajo": "Test OT"}}},
                headers=auth_headers,
            )
            assert wo.status_code == 201, f"Crear OT falló: {wo.text}"
            ot_id = wo.json()["data"]["id"]

            # =================================================================
            # Paso 1: CREAR intervención
            # =================================================================
            create_payload = {
                "data": {
                    "type": "intervenciones",
                    "attributes": {
                        "work_order_id": ot_id,
                        "technician_id": usuario_id,
                        "tareas_realizadas": "Revisión de motor eléctrico",
                        "fecha_inicio": "2026-06-28T10:00:00",  # timezone-naive para TIMESTAMP sin zona
                        "horas_hombre": 3.5,
                    },
                }
            }
            res_create = await client.post(
                f"/v1/empresas/{empresa_id}/ordenes-trabajo/{ot_id}/intervenciones",
                json=create_payload,
                headers=auth_headers,
            )
            assert res_create.status_code == 201, f"Crear intervención falló: {res_create.text}"
            int_data = res_create.json()["data"]
            int_id = int_data["id"]
            attrs = int_data["attributes"]
            assert attrs["tareas_realizadas"] == "Revisión de motor eléctrico"
            assert attrs["horas_hombre"] == 3.5
            assert attrs["fecha_fin"] is None

            # =================================================================
            # Paso 2: OBTENER intervención por ID
            # =================================================================
            res_get = await client.get(
                f"/v1/empresas/{empresa_id}/ordenes-trabajo/{ot_id}/intervenciones/{int_id}",
                headers=auth_headers,
            )
            assert res_get.status_code == 200
            assert res_get.json()["data"]["attributes"]["tareas_realizadas"] == "Revisión de motor eléctrico"

            # =================================================================
            # Paso 3: LISTAR intervenciones
            # =================================================================
            res_list = await client.get(
                f"/v1/empresas/{empresa_id}/ordenes-trabajo/{ot_id}/intervenciones",
                headers=auth_headers,
            )
            assert res_list.status_code == 200
            assert res_list.json()["meta"]["total"] >= 1
            ids = [r["id"] for r in res_list.json()["data"]]
            assert int_id in ids

            # =================================================================
            # Paso 4: ACTUALIZAR intervención
            # =================================================================
            update_payload = {
                "data": {
                    "type": "intervenciones",
                    "id": int_id,
                    "attributes": {
                        "tareas_realizadas": "Trabajo completado - motor reparado",
                        "horas_hombre": 4.0,
                    },
                }
            }
            res_update = await client.patch(
                f"/v1/empresas/{empresa_id}/ordenes-trabajo/{ot_id}/intervenciones/{int_id}",
                json=update_payload,
                headers=auth_headers,
            )
            assert res_update.status_code == 200, f"Actualizar intervención falló: {res_update.text}"
            assert res_update.json()["data"]["attributes"]["tareas_realizadas"] == "Trabajo completado - motor reparado"
            assert res_update.json()["data"]["attributes"]["horas_hombre"] == 4.0

            # =================================================================
            # CONFIG: Registrar Compañía B
            # =================================================================
            id_b = uuid.uuid4().hex[:8]
            reg_b = {
                "data": {
                    "type": "users",
                    "attributes": {
                        "email": f"admin_b_{id_b}@example.com",
                        "password": password,
                        "nombre": "Admin B",
                        "company_name": f"Company B {id_b}",
                        "telefono": "+2222222222",
                    },
                }
            }
            res_b = await client.post("/v1/auth/registrar", json=reg_b, headers=headers)
            assert res_b.status_code == 201
            tokens_b = res_b.json()["data"]["attributes"]
            auth_headers_b = {**headers, "Authorization": f"Bearer {tokens_b['access_token']}"}
            res_me_b = await client.get("/v1/auth/yo", headers=auth_headers_b)
            empresa_b_id = res_me_b.json()["data"]["attributes"]["empresa_id"]

            # =================================================================
            # Paso 5: AISLAMIENTO MULTI-TENANT
            # =================================================================
            # Token B accediendo a ruta de Empresa A → 403
            res_403 = await client.get(
                f"/v1/empresas/{empresa_id}/ordenes-trabajo/{ot_id}/intervenciones/{int_id}",
                headers=auth_headers_b,
            )
            assert res_403.status_code == 403

            # Token B buscando en su tenant la intervención de A → 404
            res_404 = await client.get(
                f"/v1/empresas/{empresa_b_id}/ordenes-trabajo/{ot_id}/intervenciones/{int_id}",
                headers=auth_headers_b,
            )
            assert res_404.status_code == 404

    finally:
        app.dependency_overrides.clear()
