import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.presentation.api.v1.endpoints.dependencies import rate_limit_by_email


@pytest.mark.asyncio
async def test_work_orders_crud_and_isolation_flow():
    """Test E2E para verificar CRUD, máquina de estados y aislamiento multi-tenant de órdenes de trabajo."""
    # 1. Desactivar rate limiting para el test
    app.dependency_overrides[rate_limit_by_email] = lambda: None

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            headers = {
                "Content-Type": "application/vnd.api+json",
                "Accept": "application/vnd.api+json",
            }

            # =====================================================================
            # CONFIGURACIÓN: Registrar Compañía A y obtener credenciales
            # =====================================================================
            id_a = uuid.uuid4().hex[:8]
            email_a = f"admin_a_{id_a}@example.com"
            company_a_name = f"Company A {id_a}"
            password = "Password123!"

            reg_payload_a = {
                "data": {
                    "type": "users",
                    "attributes": {
                        "email": email_a,
                        "password": password,
                        "nombre": "Admin Company A",
                        "company_name": company_a_name,
                        "telefono": "+1111111111",
                    },
                }
            }
            res_reg_a = await client.post("/v1/auth/registrar", json=reg_payload_a, headers=headers)
            assert res_reg_a.status_code == 201, f"Registro A fallido: {res_reg_a.text}"
            tokens_a = res_reg_a.json()["data"]["attributes"]
            access_token_a = tokens_a["access_token"]

            # Obtener empresa_id de la Compañía A desde perfil
            auth_headers_a = {**headers, "Authorization": f"Bearer {access_token_a}"}
            res_me_a = await client.get("/v1/auth/yo", headers=auth_headers_a)
            empresa_a_id = res_me_a.json()["data"]["attributes"]["empresa_id"]

            # =====================================================================
            # SEED: Crear categoría de artículo
            # =====================================================================
            cat_payload = {
                "data": {
                    "type": "article_categories",
                    "attributes": {
                        "name": "Componentes Eléctricos",
                        "description": "Categoría de prueba",
                    },
                }
            }
            res_cat = await client.post(
                f"/v1/empresas/{empresa_a_id}/catalogo/categorias",
                json=cat_payload,
                headers=auth_headers_a,
            )
            assert res_cat.status_code == 201, f"Crear categoría falló: {res_cat.text}"
            category_id = res_cat.json()["data"]["id"]

            # =====================================================================
            # SEED: Crear artículo de catálogo
            # =====================================================================
            article_payload = {
                "data": {
                    "type": "catalog-articles",
                    "attributes": {
                        "category_id": category_id,
                        "name": "Motor Eléctrico 5HP",
                        "description": "Motor trifásico de 5HP para pruebas",
                        "manufacturer": "Siemens",
                        "model": "1LE1003-1DA4",
                        "unit_of_measure": "unidad",
                    },
                }
            }
            res_article = await client.post(
                f"/v1/empresas/{empresa_a_id}/catalogo/articulos",
                json=article_payload,
                headers=auth_headers_a,
            )
            assert res_article.status_code == 201, f"Crear artículo falló: {res_article.text}"
            articulo_id = res_article.json()["data"]["id"]

            # =====================================================================
            # SEED: Crear activo
            # =====================================================================
            asset_payload = {
                "data": {
                    "type": "assets",
                    "attributes": {
                        "articulo_id": articulo_id,
                        "serial_interno": f"SN-{id_a}-001",
                        "codigo_activo": f"ACT-{id_a}-001",
                        "estado": "operativo",
                    },
                }
            }
            res_asset = await client.post(
                f"/v1/empresas/{empresa_a_id}/activos",
                json=asset_payload,
                headers=auth_headers_a,
            )
            assert res_asset.status_code == 201, f"Crear activo falló: {res_asset.text}"
            activo_id = res_asset.json()["data"]["id"]

            # =====================================================================
            # Paso 1: CREAR una orden de trabajo (POST)
            # =====================================================================
            create_payload = {
                "data": {
                    "type": "work_orders",
                    "attributes": {
                        "activo_id": activo_id,
                        "tipo": "correctivo",
                        "descripcion_trabajo": "Revisar motor eléctrico por sobrecalentamiento",
                        "costo_estimado": 1500.00,
                        "moneda": "USD",
                    },
                }
            }
            res_create = await client.post(
                f"/v1/empresas/{empresa_a_id}/ordenes-trabajo",
                json=create_payload,
                headers=auth_headers_a,
            )
            assert res_create.status_code == 201, f"Crear OT falló: {res_create.text}"
            wo_data = res_create.json()["data"]
            wo_id = wo_data["id"]
            wo_attrs = wo_data["attributes"]

            # Validar inicialización de campos y estado por defecto
            assert wo_attrs["codigo_ot"] is not None
            assert wo_attrs["tipo"] == "correctivo"
            assert wo_attrs["estado"] == "abierta"
            assert wo_attrs["descripcion_trabajo"] == "Revisar motor eléctrico por sobrecalentamiento"
            assert wo_attrs["costo_estimado"] == 1500.0
            assert wo_attrs["moneda"] == "USD"
            assert wo_attrs["activo_id"] == activo_id
            assert "fecha_apertura" in wo_attrs

            # =====================================================================
            # Paso 2: OBTENER la orden de trabajo por su ID (GET)
            # =====================================================================
            res_get = await client.get(
                f"/v1/empresas/{empresa_a_id}/ordenes-trabajo/{wo_id}",
                headers=auth_headers_a,
            )
            assert res_get.status_code == 200
            assert res_get.json()["data"]["attributes"]["estado"] == "abierta"
            assert res_get.json()["data"]["attributes"]["tipo"] == "correctivo"

            # =====================================================================
            # Paso 3: LISTAR órdenes de trabajo (GET)
            # =====================================================================
            res_list = await client.get(
                f"/v1/empresas/{empresa_a_id}/ordenes-trabajo?estado=abierta",
                headers=auth_headers_a,
            )
            assert res_list.status_code == 200
            list_data = res_list.json()
            assert list_data["meta"]["total"] >= 1
            wo_ids = [r["id"] for r in list_data["data"]]
            assert wo_id in wo_ids

            # =====================================================================
            # Paso 4: CAMBIAR ESTADO a "en_proceso" (PATCH .../estado)
            # =====================================================================
            status_payload = {
                "data": {
                    "type": "work_orders",
                    "attributes": {
                        "estado": "en_proceso",
                    },
                }
            }
            res_status = await client.patch(
                f"/v1/empresas/{empresa_a_id}/ordenes-trabajo/{wo_id}/estado",
                json=status_payload,
                headers=auth_headers_a,
            )
            assert res_status.status_code == 200, f"Cambio estado falló: {res_status.text}"
            assert res_status.json()["data"]["attributes"]["estado"] == "en_proceso"
            assert "fecha_inicio_trabajo" in res_status.json()["data"]["attributes"]

            # Cambiar a "pausada"
            status_payload["data"]["attributes"]["estado"] = "pausada"
            res_status = await client.patch(
                f"/v1/empresas/{empresa_a_id}/ordenes-trabajo/{wo_id}/estado",
                json=status_payload,
                headers=auth_headers_a,
            )
            assert res_status.status_code == 200
            assert res_status.json()["data"]["attributes"]["estado"] == "pausada"

            # Reanudar a "en_proceso"
            status_payload["data"]["attributes"]["estado"] = "en_proceso"
            res_status = await client.patch(
                f"/v1/empresas/{empresa_a_id}/ordenes-trabajo/{wo_id}/estado",
                json=status_payload,
                headers=auth_headers_a,
            )
            assert res_status.status_code == 200
            assert res_status.json()["data"]["attributes"]["estado"] == "en_proceso"

            # Cerrar orden
            status_payload["data"]["attributes"]["estado"] = "cerrada"
            res_status = await client.patch(
                f"/v1/empresas/{empresa_a_id}/ordenes-trabajo/{wo_id}/estado",
                json=status_payload,
                headers=auth_headers_a,
            )
            assert res_status.status_code == 200
            assert res_status.json()["data"]["attributes"]["estado"] == "cerrada"
            assert "fecha_cierre" in res_status.json()["data"]["attributes"]

            # =====================================================================
            # Paso 5: ACTUALIZAR detalles de la orden (PATCH)
            # =====================================================================
            update_payload = {
                "data": {
                    "type": "work_orders",
                    "attributes": {
                        "descripcion_trabajo": "Trabajo completado - motor reemplazado",
                        "costo_real": 1800.00,
                    },
                }
            }
            res_update = await client.patch(
                f"/v1/empresas/{empresa_a_id}/ordenes-trabajo/{wo_id}",
                json=update_payload,
                headers=auth_headers_a,
            )
            assert res_update.status_code == 200, f"Actualizar OT falló: {res_update.text}"
            assert res_update.json()["data"]["attributes"]["descripcion_trabajo"] == "Trabajo completado - motor reemplazado"
            assert res_update.json()["data"]["attributes"]["costo_real"] == 1800.0

            # =====================================================================
            # CONFIGURACIÓN: Registrar Compañía B
            # =====================================================================
            id_b = uuid.uuid4().hex[:8]
            email_b = f"admin_b_{id_b}@example.com"
            company_b_name = f"Company B {id_b}"

            reg_payload_b = {
                "data": {
                    "type": "users",
                    "attributes": {
                        "email": email_b,
                        "password": password,
                        "nombre": "Admin Company B",
                        "company_name": company_b_name,
                        "telefono": "+2222222222",
                    },
                }
            }
            res_reg_b = await client.post("/v1/auth/registrar", json=reg_payload_b, headers=headers)
            assert res_reg_b.status_code == 201
            tokens_b = res_reg_b.json()["data"]["attributes"]
            access_token_b = tokens_b["access_token"]
            auth_headers_b = {**headers, "Authorization": f"Bearer {access_token_b}"}
            res_me_b = await client.get("/v1/auth/yo", headers=auth_headers_b)
            empresa_b_id = res_me_b.json()["data"]["attributes"]["empresa_id"]

            # =====================================================================
            # Paso 6: AISLAMIENTO MULTI-TENANT (IDOR)
            # =====================================================================
            # Caso A: Token B accediendo a ruta de Empresa A (HTTP 403)
            res_cross_tenant = await client.get(
                f"/v1/empresas/{empresa_a_id}/ordenes-trabajo/{wo_id}",
                headers=auth_headers_b,
            )
            assert res_cross_tenant.status_code == 403

            # Caso B: Token B buscando en su propio tenant la OT de A (HTTP 404)
            res_cross_tenant_real = await client.get(
                f"/v1/empresas/{empresa_b_id}/ordenes-trabajo/{wo_id}",
                headers=auth_headers_b,
            )
            assert res_cross_tenant_real.status_code == 404

            # =====================================================================
            # Paso 7: ELIMINAR la orden de trabajo (DELETE)
            # =====================================================================
            res_delete = await client.delete(
                f"/v1/empresas/{empresa_a_id}/ordenes-trabajo/{wo_id}",
                headers=auth_headers_a,
            )
            assert res_delete.status_code == 204

            # Verificar que obtener la orden borrada retorna HTTP 404
            res_get_deleted = await client.get(
                f"/v1/empresas/{empresa_a_id}/ordenes-trabajo/{wo_id}",
                headers=auth_headers_a,
            )
            assert res_get_deleted.status_code == 404

    finally:
        app.dependency_overrides.clear()
