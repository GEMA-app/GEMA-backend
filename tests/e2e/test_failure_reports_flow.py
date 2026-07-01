import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.presentation.api.v1.endpoints.dependencies import rate_limit_by_email


@pytest.mark.asyncio
async def test_failure_reports_crud_and_concurrency_flow():
    """Test E2E para verificar el CRUD, control de concurrencia e isolation de reportes de falla."""
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
            # Paso 1: CREAR un reporte de falla en Compañía A (POST)
            # =====================================================================
            create_payload = {
                "data": {
                    "type": "failure-reports",
                    "attributes": {
                        "title": "Bomba de Agua rota",
                        "description": "Fuga severa en sello mecánico de la bomba principal B-101",
                        "location": "Planta 1 - Sector Hidráulico",
                        "priority": "alta",
                        "reported_by": "Ing. Carlos Mendoza",
                    },
                }
            }
            res_create = await client.post(
                f"/v1/empresas/{empresa_a_id}/reportes-fallas",
                json=create_payload,
                headers=auth_headers_a,
            )
            assert res_create.status_code == 201, f"Creación de reporte fallida: {res_create.text}"
            report_data = res_create.json()["data"]
            reporte_id = report_data["id"]
            attrs = report_data["attributes"]

            # Validar inicialización de campos y versión por defecto
            assert attrs["title"] == "Bomba de Agua rota"
            assert attrs["description"] == "Fuga severa en sello mecánico de la bomba principal B-101"
            assert attrs["location"] == "Planta 1 - Sector Hidráulico"
            assert attrs["priority"] == "alta"
            assert attrs["reported_by"] == "Ing. Carlos Mendoza"
            assert attrs["status"] == "pendiente"
            assert attrs["version"] == 1
            assert "created_at" in attrs

            # =====================================================================
            # Paso 2: OBTENER el reporte creado por su ID (GET)
            # =====================================================================
            res_get = await client.get(
                f"/v1/empresas/{empresa_a_id}/reportes-fallas/{reporte_id}",
                headers=auth_headers_a,
            )
            assert res_get.status_code == 200
            assert res_get.json()["data"]["attributes"]["title"] == "Bomba de Agua rota"
            assert res_get.json()["data"]["attributes"]["version"] == 1

            # =====================================================================
            # Paso 3: LISTAR reportes con paginación y filtros (GET)
            # =====================================================================
            res_list = await client.get(
                f"/v1/empresas/{empresa_a_id}/reportes-fallas?status=pendiente&priority=alta",
                headers=auth_headers_a,
            )
            assert res_list.status_code == 200
            list_data = res_list.json()
            assert list_data["meta"]["total"] >= 1
            reports_ids = [r["id"] for r in list_data["data"]]
            assert reporte_id in reports_ids

            # =====================================================================
            # Paso 4: ACTUALIZAR parcialmente el reporte (PATCH)
            # =====================================================================
            update_payload = {
                "data": {
                    "type": "failure-reports",
                    "attributes": {
                        "status": "en_proceso",
                        "version": 1,  # Enviamos versión 1 correcta
                    },
                }
            }
            res_patch = await client.patch(
                f"/v1/empresas/{empresa_a_id}/reportes-fallas/{reporte_id}",
                json=update_payload,
                headers=auth_headers_a,
            )
            assert res_patch.status_code == 200, f"Actualización fallida: {res_patch.text}"
            assert res_patch.json()["data"]["attributes"]["status"] == "en_proceso"
            assert res_patch.json()["data"]["attributes"]["version"] == 2  # Versión incrementada

            # =====================================================================
            # Paso 5: CONTROL DE CONCURRENCIA (StaleDataError - HTTP 409)
            # =====================================================================
            stale_update_payload = {
                "data": {
                    "type": "failure-reports",
                    "attributes": {
                        "description": "Edición concurrente conflictiva",
                        "version": 1,  # Enviamos versión obsoleta (la actual en DB es 2)
                    },
                }
            }
            res_stale = await client.patch(
                f"/v1/empresas/{empresa_a_id}/reportes-fallas/{reporte_id}",
                json=stale_update_payload,
                headers=auth_headers_a,
            )
            assert res_stale.status_code == 409
            assert "Conflicto" in res_stale.json()["errors"][0]["detail"]

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

            # =====================================================================
            # Paso 6: AISLAMIENTO MULTI-TENANT (IDOR)
            # =====================================================================
            # Caso A: Intentar usar path de Empresa A con token de Empresa B (HTTP 403)
            res_cross_tenant_path = await client.get(
                f"/v1/empresas/{empresa_a_id}/reportes-fallas/{reporte_id}",
                headers=auth_headers_b,
            )
            assert res_cross_tenant_path.status_code == 403

            # Caso B: Intentar solicitar reporte de Empresa A usando path de Empresa B (HTTP 404)
            await client.get(
                f"/v1/empresas/{empresa_a_id}/reportes-fallas/{reporte_id}".replace(empresa_a_id, tokens_b.get("empresa_id", "") or "00000000-0000-0000-0000-000000000000"),
                headers=auth_headers_b,
            )
            # Nota: si el campo empresa_id del token se puede obtener del /yo de B
            res_me_b = await client.get("/v1/auth/yo", headers=auth_headers_b)
            empresa_b_id = res_me_b.json()["data"]["attributes"]["empresa_id"]

            res_cross_tenant_report_real = await client.get(
                f"/v1/empresas/{empresa_b_id}/reportes-fallas/{reporte_id}",
                headers=auth_headers_b,
            )
            assert res_cross_tenant_report_real.status_code == 404

            # =====================================================================
            # Paso 7: ELIMINAR el reporte de falla (DELETE)
            # =====================================================================
            res_delete = await client.delete(
                f"/v1/empresas/{empresa_a_id}/reportes-fallas/{reporte_id}",
                headers=auth_headers_a,
            )
            assert res_delete.status_code == 204

            # Verificar que obtener el reporte borrado retorna HTTP 404
            res_get_deleted = await client.get(
                f"/v1/empresas/{empresa_a_id}/reportes-fallas/{reporte_id}",
                headers=auth_headers_a,
            )
            assert res_get_deleted.status_code == 404

    finally:
        app.dependency_overrides.clear()
