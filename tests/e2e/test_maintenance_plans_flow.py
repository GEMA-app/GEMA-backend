import uuid
from datetime import date

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.presentation.api.v1.endpoints.dependencies import rate_limit_by_email


@pytest.mark.asyncio
async def test_maintenance_plans_crud_and_isolation_flow():
    """Test E2E para verificar CRUD, filtros y aislamiento multi-tenant de planes de mantenimiento."""
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
                        "name": "Bombas Hidráulicas",
                        "description": "Categoría para planes de prueba",
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
                        "name": "Bomba de Recirculación",
                        "description": "Bomba de recirculación centrífuga",
                        "manufacturer": "Wilo",
                        "model": "Star-RS 25/4",
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
                        "serial_interno": f"SN-PLAN-{id_a}",
                        "codigo_activo": f"ACT-PLAN-{id_a}",
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
            # Paso 1: CREAR un plan de mantenimiento (POST)
            # =====================================================================
            plan_payload = {
                "data": {
                    "type": "maintenance-plans",
                    "attributes": {
                        "activo_id": activo_id,
                        "nombre": "Plan de Mantenimiento Trimestral de Bomba Wilo",
                        "tipo": "preventivo",
                        "intervalo_dias": 90,
                        "proxima_ejecucion": "2026-09-30",
                        "tecnico_responsable_id": None,
                        "descripcion_tareas": "Verificar ruidos, purgar aire, comprobar corriente absorbida.",
                    },
                }
            }
            res_create = await client.post(
                f"/v1/empresas/{empresa_a_id}/planes-mantenimiento",
                json=plan_payload,
                headers=auth_headers_a,
            )
            assert res_create.status_code == 201, f"Crear plan falló: {res_create.text}"
            plan_data = res_create.json()["data"]
            plan_id = plan_data["id"]
            plan_attrs = plan_data["attributes"]

            # Validar campos iniciales
            assert plan_attrs["nombre"] == "Plan de Mantenimiento Trimestral de Bomba Wilo"
            assert plan_attrs["tipo"] == "preventivo"
            assert plan_attrs["intervalo_dias"] == 90
            assert plan_attrs["proxima_ejecucion"] == "2026-09-30"
            assert plan_attrs["activo_id"] == activo_id
            assert plan_attrs["activo"] is True
            assert plan_attrs["descripcion_tareas"] == "Verificar ruidos, purgar aire, comprobar corriente absorbida."
            assert "created_at" in plan_attrs

            # =====================================================================
            # Paso 2: OBTENER el plan de mantenimiento por su ID (GET)
            # =====================================================================
            res_get = await client.get(
                f"/v1/empresas/{empresa_a_id}/planes-mantenimiento/{plan_id}",
                headers=auth_headers_a,
            )
            assert res_get.status_code == 200
            assert res_get.json()["data"]["attributes"]["nombre"] == "Plan de Mantenimiento Trimestral de Bomba Wilo"
            assert res_get.json()["data"]["attributes"]["activo"] is True

            # =====================================================================
            # Paso 3: LISTAR planes de mantenimiento con filtros (GET)
            # =====================================================================
            res_list = await client.get(
                f"/v1/empresas/{empresa_a_id}/planes-mantenimiento?activo_id={activo_id}&tipo=preventivo&activo=true",
                headers=auth_headers_a,
            )
            assert res_list.status_code == 200
            list_data = res_list.json()
            assert list_data["meta"]["total"] >= 1
            plan_ids = [r["id"] for r in list_data["data"]]
            assert plan_id in plan_ids

            # =====================================================================
            # Paso 4: ACTUALIZAR el plan de mantenimiento (PATCH)
            # =====================================================================
            update_payload = {
                "data": {
                    "type": "maintenance-plans",
                    "attributes": {
                        "nombre": "Plan de Mantenimiento Trimestral Wilo - Modificado",
                        "intervalo_dias": 120,
                        "activo": False,
                    },
                }
            }
            res_update = await client.patch(
                f"/v1/empresas/{empresa_a_id}/planes-mantenimiento/{plan_id}",
                json=update_payload,
                headers=auth_headers_a,
            )
            assert res_update.status_code == 200, f"Actualizar plan falló: {res_update.text}"
            updated_attrs = res_update.json()["data"]["attributes"]
            assert updated_attrs["nombre"] == "Plan de Mantenimiento Trimestral Wilo - Modificado"
            assert updated_attrs["intervalo_dias"] == 120
            assert updated_attrs["activo"] is False

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
            # Paso 5: AISLAMIENTO MULTI-TENANT (IDOR)
            # =====================================================================
            # Caso A: Token B accediendo a ruta de Empresa A (HTTP 403)
            res_cross_tenant = await client.get(
                f"/v1/empresas/{empresa_a_id}/planes-mantenimiento/{plan_id}",
                headers=auth_headers_b,
            )
            assert res_cross_tenant.status_code == 403

            # Caso B: Token B buscando en su propio tenant el plan de A (HTTP 404)
            res_cross_tenant_real = await client.get(
                f"/v1/empresas/{empresa_b_id}/planes-mantenimiento/{plan_id}",
                headers=auth_headers_b,
            )
            assert res_cross_tenant_real.status_code == 404

            # =====================================================================
            # Paso 6: ELIMINAR el plan de mantenimiento (DELETE)
            # =====================================================================
            res_delete = await client.delete(
                f"/v1/empresas/{empresa_a_id}/planes-mantenimiento/{plan_id}",
                headers=auth_headers_a,
            )
            assert res_delete.status_code == 204

            # Verificar que obtener el plan borrado retorna HTTP 404
            res_get_deleted = await client.get(
                f"/v1/empresas/{empresa_a_id}/planes-mantenimiento/{plan_id}",
                headers=auth_headers_a,
            )
            assert res_get_deleted.status_code == 404

    finally:
        app.dependency_overrides.clear()
