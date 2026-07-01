"""Test E2E para CRUD de activos con aislamiento multi-tenant."""

import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.presentation.api.v1.endpoints.dependencies import rate_limit_by_email


@pytest.mark.asyncio
async def test_assets_crud_flow():
    """CRUD de activos + tenant isolation."""
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

            # Crear categoría de artículo
            cat_suffix = uuid.uuid4().hex[:8]
            res = await client.post(f"/v1/empresas/{empresa_id}/catalogo/categorias", json={
                "data": {"type": "article_categories", "attributes": {
                    "name": f"Equipos {cat_suffix}",
                    "description": "Categoría de equipos",
                }},
            }, headers=auth)
            assert res.status_code == 201, f"Create categoría falló: {res.text}"
            cat_id = res.json()["data"]["id"]

            # Crear artículo de catálogo
            art_suffix = uuid.uuid4().hex[:8]
            res = await client.post(f"/v1/empresas/{empresa_id}/catalogo/articulos", json={
                "data": {"type": "catalog-articles", "attributes": {
                    "name": f"Laptop {art_suffix}",
                    "description": "Laptop corporativa",
                    "category_id": cat_id,
                    "unit_of_measure": "unidad",
                }},
            }, headers=auth)
            assert res.status_code == 201, f"Create artículo falló: {res.text}"
            articulo_id = res.json()["data"]["id"]

            # CREATE activo (serial se guarda en lowercase)
            serial_raw = f"ser-{uuid.uuid4().hex[:8]}"
            codigo = f"act-{uuid.uuid4().hex[:8]}"
            res = await client.post(f"/v1/empresas/{empresa_id}/activos", json={
                "data": {"type": "assets", "attributes": {
                    "articulo_id": articulo_id,
                    "serial_interno": serial_raw,
                    "codigo_activo": codigo,
                    "estado": "operativo",
                    "moneda": "USD",
                }},
            }, headers=auth)
            assert res.status_code == 201, f"Create activo falló: {res.text}"
            activo_id = res.json()["data"]["id"]
            assert res.json()["data"]["attributes"]["estado"] == "operativo"

            # LIST activos
            res = await client.get(f"/v1/empresas/{empresa_id}/activos", headers=auth)
            assert res.status_code == 200
            activo_ids = [a["id"] for a in res.json()["data"]]
            assert activo_id in activo_ids

            # GET by ID
            res = await client.get(f"/v1/empresas/{empresa_id}/activos/{activo_id}", headers=auth)
            assert res.status_code == 200
            assert res.json()["data"]["attributes"]["serial_interno"] == serial_raw

            # UPDATE activo (cambiar estado)
            res = await client.patch(f"/v1/empresas/{empresa_id}/activos/{activo_id}", json={
                "data": {"type": "assets", "attributes": {
                    "estado": "en_mantenimiento",
                    "version": 1,
                }},
            }, headers=auth)
            assert res.status_code == 200, f"Update activo falló: {res.text}"
            assert res.json()["data"]["attributes"]["estado"] == "en_mantenimiento"

            # DELETE activo
            res = await client.delete(f"/v1/empresas/{empresa_id}/activos/{activo_id}", headers=auth)
            assert res.status_code == 204

            # Verificar eliminado
            res = await client.get(f"/v1/empresas/{empresa_id}/activos", headers=auth)
            assert activo_id not in [a["id"] for a in res.json()["data"]]

    finally:
        app.dependency_overrides.clear()
