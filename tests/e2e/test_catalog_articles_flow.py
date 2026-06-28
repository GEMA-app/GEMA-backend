"""Test E2E para verificar el CRUD e isolation multi-tenant de los Artículos de Catálogo (CatalogArticle)."""

import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.presentation.api.v1.endpoints.dependencies import rate_limit_by_email


@pytest.mark.asyncio
async def test_catalog_articles_crud_and_isolation_flow() -> None:
    """Test E2E para verificar el CRUD e isolation multi-tenant de Artículos de Catálogo."""
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
            # PREREQUISITO: Crear una categoría en Compañía A (FK necesaria)
            # =====================================================================
            cat_payload = {
                "data": {
                    "type": "article_categories",
                    "attributes": {
                        "name": "Herramientas Eléctricas",
                        "description": "Taladros, sierras, amoladoras, etc.",
                    },
                }
            }
            res_cat = await client.post(
                f"/v1/empresas/{empresa_a_id}/catalogo/categorias",
                json=cat_payload,
                headers=auth_headers_a,
            )
            assert res_cat.status_code == 201, f"Creación de categoría fallida: {res_cat.text}"
            category_id = res_cat.json()["data"]["id"]

            # =====================================================================
            # Paso 1: CREAR un artículo de catálogo en Compañía A (POST)
            # =====================================================================
            create_payload = {
                "data": {
                    "type": "catalog-articles",
                    "attributes": {
                        "category_id": category_id,
                        "name": "Taladro Percutor Profesional",
                        "description": "Taladro percutor 220V con SDS-plus",
                        "manufacturer": "Bosch",
                        "model": "GBH 2-28 F",
                        "unit_of_measure": "UNIDAD",
                    },
                }
            }
            res_create = await client.post(
                f"/v1/empresas/{empresa_a_id}/catalogo/articulos",
                json=create_payload,
                headers=auth_headers_a,
            )
            assert res_create.status_code == 201, f"Creación fallida: {res_create.text}"
            data_create = res_create.json()["data"]
            article_id = data_create["id"]
            attrs = data_create["attributes"]

            assert attrs["name"] == "Taladro Percutor Profesional"
            assert attrs["description"] == "Taladro percutor 220V con SDS-plus"
            assert attrs["manufacturer"] == "Bosch"
            assert attrs["model"] == "GBH 2-28 F"
            assert attrs["unit_of_measure"] == "UNIDAD"
            assert attrs["category_id"] == category_id
            assert attrs["empresa_id"] == empresa_a_id

            # =====================================================================
            # Paso 2: OBTENER el artículo creado por ID (GET)
            # =====================================================================
            res_get = await client.get(
                f"/v1/empresas/{empresa_a_id}/catalogo/articulos/{article_id}",
                headers=auth_headers_a,
            )
            assert res_get.status_code == 200
            data_get = res_get.json()["data"]
            assert data_get["id"] == article_id
            assert data_get["attributes"]["name"] == "Taladro Percutor Profesional"

            # =====================================================================
            # Paso 3: LISTAR artículos y verificar que incluye el creado
            # =====================================================================
            res_list = await client.get(
                f"/v1/empresas/{empresa_a_id}/catalogo/articulos",
                headers=auth_headers_a,
            )
            assert res_list.status_code == 200
            list_data = res_list.json()["data"]
            assert len(list_data) >= 1
            article_ids = [item["id"] for item in list_data]
            assert article_id in article_ids

            # =====================================================================
            # Paso 4: LISTAR con filtro por categoría (category_id)
            # =====================================================================
            res_filter = await client.get(
                f"/v1/empresas/{empresa_a_id}/catalogo/articulos",
                params={"category_id": category_id},
                headers=auth_headers_a,
            )
            assert res_filter.status_code == 200
            filtered = res_filter.json()["data"]
            assert len(filtered) >= 1
            assert all(
                item["attributes"]["category_id"] == category_id for item in filtered
            )

            # =====================================================================
            # Paso 5: LISTAR con búsqueda por nombre (search)
            # =====================================================================
            res_search = await client.get(
                f"/v1/empresas/{empresa_a_id}/catalogo/articulos",
                params={"search": "Taladro"},
                headers=auth_headers_a,
            )
            assert res_search.status_code == 200
            searched = res_search.json()["data"]
            assert len(searched) >= 1
            assert searched[0]["attributes"]["name"] == "Taladro Percutor Profesional"

            # =====================================================================
            # Paso 6: Validar nombre vacío → 422 (EmptyCatalogArticleNameError)
            # =====================================================================
            invalid_payload = {
                "data": {
                    "type": "catalog-articles",
                    "attributes": {
                        "name": "   ",
                        "description": "Inválida",
                    },
                }
            }
            res_invalid = await client.post(
                f"/v1/empresas/{empresa_a_id}/catalogo/articulos",
                json=invalid_payload,
                headers=auth_headers_a,
            )
            assert res_invalid.status_code == 422
            assert "ERR_EMPTY_CATALOG_ARTICLE_NAME" in res_invalid.text

            # =====================================================================
            # Paso 7: Validar category_id inexistente → 409 (IntegrityError)
            # =====================================================================
            fake_category = "00000000-0000-0000-0000-000000000000"
            bad_fk_payload = {
                "data": {
                    "type": "catalog-articles",
                    "attributes": {
                        "name": "Artículo con FK inválida",
                        "category_id": fake_category,
                    },
                }
            }
            res_bad_fk = await client.post(
                f"/v1/empresas/{empresa_a_id}/catalogo/articulos",
                json=bad_fk_payload,
                headers=auth_headers_a,
            )
            assert res_bad_fk.status_code == 409, (
                f"FK inválida status={res_bad_fk.status_code}: {res_bad_fk.text}"
            )
            assert "ERR_DB_INTEGRITY" in res_bad_fk.text

            # =====================================================================
            # Paso 8: Aislamiento MULTI-TENANT (Compañía B no puede acceder/modificar)
            # =====================================================================
            # B intenta obtener el artículo de A (debería dar 403)
            res_get_b = await client.get(
                f"/v1/empresas/{empresa_a_id}/catalogo/articulos/{article_id}",
                headers=auth_headers_b,
            )
            assert res_get_b.status_code == 403

            # B intenta modificar el artículo de A
            patch_payload_b = {
                "data": {
                    "type": "catalog-articles",
                    "attributes": {
                        "name": "Artículo Robado",
                    },
                }
            }
            res_patch_b = await client.patch(
                f"/v1/empresas/{empresa_a_id}/catalogo/articulos/{article_id}",
                json=patch_payload_b,
                headers=auth_headers_b,
            )
            assert res_patch_b.status_code == 403

            # B intenta eliminar el artículo de A
            res_delete_b = await client.delete(
                f"/v1/empresas/{empresa_a_id}/catalogo/articulos/{article_id}",
                headers=auth_headers_b,
            )
            assert res_delete_b.status_code == 403

            # =====================================================================
            # Paso 9: ACTUALIZAR el artículo (PATCH)
            # =====================================================================
            update_payload = {
                "data": {
                    "type": "catalog-articles",
                    "attributes": {
                        "description": "Taladro SDS-plus con mandril rápido",
                        "manufacturer": "Bosch Professional",
                    },
                }
            }
            res_update = await client.patch(
                f"/v1/empresas/{empresa_a_id}/catalogo/articulos/{article_id}",
                json=update_payload,
                headers=auth_headers_a,
            )
            assert res_update.status_code == 200
            data_update = res_update.json()["data"]
            assert (
                data_update["attributes"]["description"]
                == "Taladro SDS-plus con mandril rápido"
            )
            assert data_update["attributes"]["manufacturer"] == "Bosch Professional"
            # Los campos no enviados deben permanecer igual
            assert data_update["attributes"]["name"] == "Taladro Percutor Profesional"
            assert data_update["attributes"]["model"] == "GBH 2-28 F"
            assert data_update["attributes"]["unit_of_measure"] == "UNIDAD"

            # =====================================================================
            # Paso 10: ELIMINAR el artículo (DELETE)
            # =====================================================================
            res_delete = await client.delete(
                f"/v1/empresas/{empresa_a_id}/catalogo/articulos/{article_id}",
                headers=auth_headers_a,
            )
            assert res_delete.status_code == 204

            # =====================================================================
            # Paso 11: VERIFICAR que el artículo ya no existe
            # =====================================================================
            res_get_deleted = await client.get(
                f"/v1/empresas/{empresa_a_id}/catalogo/articulos/{article_id}",
                headers=auth_headers_a,
            )
            assert res_get_deleted.status_code == 404
            assert "ERR_CATALOG_ARTICLE_NOT_FOUND" in res_get_deleted.text

    finally:
        app.dependency_overrides.clear()
