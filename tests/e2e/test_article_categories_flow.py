import uuid
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.presentation.api.v1.endpoints.dependencies import rate_limit_by_email


@pytest.mark.asyncio
async def test_article_categories_crud_and_isolation_flow():
    """Test E2E para verificar el CRUD e isolation multi-tenant de las Categorías de Artículo (ArticleCategory)."""
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
            # CONFIGURACIÓN: Registrar Compañía A y Compañía B
            # =====================================================================
            # Compañía A
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

            # Compañía B
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
            assert res_reg_b.status_code == 201, f"Registro B fallido: {res_reg_b.text}"
            tokens_b = res_reg_b.json()["data"]["attributes"]
            access_token_b = tokens_b["access_token"]

            # Obtener empresa_id de la Compañía B desde perfil
            auth_headers_b = {**headers, "Authorization": f"Bearer {access_token_b}"}
            res_me_b = await client.get("/v1/auth/yo", headers=auth_headers_b)
            empresa_b_id = res_me_b.json()["data"]["attributes"]["empresa_id"]

            # =====================================================================
            # Paso 1: CREAR una categoría en Compañía A (POST)
            # =====================================================================
            create_payload = {
                "data": {
                    "type": "article_categories",
                    "attributes": {
                        "name": "Herramientas de Mano",
                        "description": "Destornilladores, martillos, llaves, etc.",
                    },
                }
            }
            res_create = await client.post(
                f"/v1/empresas/{empresa_a_id}/catalogo/categorias",
                json=create_payload,
                headers=auth_headers_a,
            )
            assert res_create.status_code == 201, f"Creación fallida: {res_create.text}"
            data_create = res_create.json()["data"]
            category_id = data_create["id"]
            attrs = data_create["attributes"]

            assert attrs["name"] == "Herramientas de Mano"
            assert attrs["description"] == "Destornilladores, martillos, llaves, etc."
            assert attrs["empresa_id"] == empresa_a_id
            assert attrs["version"] == 1

            # =====================================================================
            # Paso 2: OBTENER la categoría creada por ID (GET)
            # =====================================================================
            res_get = await client.get(
                f"/v1/empresas/{empresa_a_id}/catalogo/categorias/{category_id}",
                headers=auth_headers_a,
            )
            assert res_get.status_code == 200
            data_get = res_get.json()["data"]
            assert data_get["id"] == category_id
            assert data_get["attributes"]["name"] == "Herramientas de Mano"

            # =====================================================================
            # Paso 3: LISTAR categorías (GET) y verificar que incluye la creada
            # =====================================================================
            res_list = await client.get(
                f"/v1/empresas/{empresa_a_id}/catalogo/categorias",
                headers=auth_headers_a,
            )
            assert res_list.status_code == 200
            list_data = res_list.json()["data"]
            assert len(list_data) >= 1
            names = [item["attributes"]["name"] for item in list_data]
            assert "Herramientas de Mano" in names

            # =====================================================================
            # Paso 4: Validar UNICIDAD del nombre dentro del tenant (409 Conflict)
            # =====================================================================
            res_duplicate = await client.post(
                f"/v1/empresas/{empresa_a_id}/catalogo/categorias",
                json=create_payload,
                headers=auth_headers_a,
            )
            assert res_duplicate.status_code == 409
            assert "ERR_ARTICLE_CATEGORY_NAME_EXISTS" in res_duplicate.text

            # =====================================================================
            # Paso 5: Validar RESTricción de nombre vacío (422 Unprocessable Content)
            # =====================================================================
            invalid_payload = {
                "data": {
                    "type": "article_categories",
                    "attributes": {
                        "name": "",
                        "description": "Inválida",
                    },
                }
            }
            res_invalid = await client.post(
                f"/v1/empresas/{empresa_a_id}/catalogo/categorias",
                json=invalid_payload,
                headers=auth_headers_a,
            )
            assert res_invalid.status_code == 422

            # =====================================================================
            # Paso 6: Aislamiento MULTI-TENANT (Compañía B no puede acceder/modificar)
            # =====================================================================
            # B intenta obtener la categoría de A (debería dar 403)
            res_get_b = await client.get(
                f"/v1/empresas/{empresa_a_id}/catalogo/categorias/{category_id}",
                headers=auth_headers_b,
            )
            assert res_get_b.status_code == 403

            # B intenta modificar la categoría de A
            patch_payload_b = {
                "data": {
                    "type": "article_categories",
                    "attributes": {
                        "name": "Herramientas Robadas",
                    },
                }
            }
            res_patch_b = await client.patch(
                f"/v1/empresas/{empresa_a_id}/catalogo/categorias/{category_id}",
                json=patch_payload_b,
                headers=auth_headers_b,
            )
            assert res_patch_b.status_code == 403

            # =====================================================================
            # Paso 7: ACTUALIZAR la categoría (PATCH)
            # =====================================================================
            update_payload = {
                "data": {
                    "type": "article_categories",
                    "attributes": {
                        "description": "Martillos, llaves, pinzas y destornilladores.",
                    },
                }
            }
            res_update = await client.patch(
                f"/v1/empresas/{empresa_a_id}/catalogo/categorias/{category_id}",
                json=update_payload,
                headers=auth_headers_a,
            )
            assert res_update.status_code == 200
            data_update = res_update.json()["data"]
            assert data_update["attributes"]["description"] == "Martillos, llaves, pinzas y destornilladores."
            assert data_update["attributes"]["name"] == "Herramientas de Mano" # Sigue igual

            # =====================================================================
            # Paso 8: ELIMINAR la categoría (DELETE)
            # =====================================================================
            res_delete = await client.delete(
                f"/v1/empresas/{empresa_a_id}/catalogo/categorias/{category_id}",
                headers=auth_headers_a,
            )
            assert res_delete.status_code == 204

            # =====================================================================
            # Paso 9: VERIFICAR que la categoría ya no existe
            # =====================================================================
            res_get_deleted = await client.get(
                f"/v1/empresas/{empresa_a_id}/catalogo/categorias/{category_id}",
                headers=auth_headers_a,
            )
            assert res_get_deleted.status_code == 404
            assert "ERR_ARTICLE_CATEGORY_NOT_FOUND" in res_get_deleted.text

    finally:
        app.dependency_overrides.clear()
