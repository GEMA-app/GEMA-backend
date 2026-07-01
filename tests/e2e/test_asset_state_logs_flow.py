"""Test E2E para historial de cambios de estado de activos."""

import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.presentation.api.v1.endpoints.dependencies import rate_limit_by_email


@pytest.mark.asyncio
async def test_asset_state_logs_flow():
    """Crear activo, cambiar estado y verificar historial."""
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

            # Crear categoría + artículo de catálogo para el activo
            cat_suffix = uuid.uuid4().hex[:8]
            res = await client.post(f"/v1/empresas/{empresa_id}/catalogo/categorias", json={
                "data": {"type": "article_categories", "attributes": {
                    "name": f"Cat {cat_suffix}",
                    "description": "Test",
                }},
            }, headers=auth)
            assert res.status_code == 201
            cat_id = res.json()["data"]["id"]

            art_suffix = uuid.uuid4().hex[:8]
            res = await client.post(f"/v1/empresas/{empresa_id}/catalogo/articulos", json={
                "data": {"type": "catalog-articles", "attributes": {
                    "name": f"Art {art_suffix}",
                    "category_id": cat_id,
                    "unit_of_measure": "unidad",
                }},
            }, headers=auth)
            assert res.status_code == 201
            articulo_id = res.json()["data"]["id"]

            # CREATE activo (estado inicial: operativo)
            serial_raw = f"ser-{uuid.uuid4().hex[:8]}"
            codigo_raw = f"act-{uuid.uuid4().hex[:8]}"
            res = await client.post(f"/v1/empresas/{empresa_id}/activos", json={
                "data": {"type": "assets", "attributes": {
                    "articulo_id": articulo_id,
                    "serial_interno": serial_raw,
                    "codigo_activo": codigo_raw,
                    "estado": "operativo",
                    "moneda": "USD",
                }},
            }, headers=auth)
            assert res.status_code == 201
            activo_id = res.json()["data"]["id"]

            # GET historial (debe tener 1 entrada: la creación)
            # Los logs se ordenan DESC por fecha_cambio, el [0] es el más reciente
            res = await client.get(
                f"/v1/empresas/{empresa_id}/activos/{activo_id}/historial-estados",
                headers=auth,
            )
            assert res.status_code == 200
            logs = res.json()["data"]
            assert len(logs) >= 1
            # El log más reciente debe tener estado_nuevo = operativo
            assert logs[0]["attributes"]["estado_nuevo"] == "operativo"

            # UPDATE activo a en_mantenimiento (genera otro log)
            res = await client.patch(f"/v1/empresas/{empresa_id}/activos/{activo_id}", json={
                "data": {"type": "assets", "attributes": {
                    "estado": "en_mantenimiento",
                    "version": 1,
                }},
            }, headers=auth)
            assert res.status_code == 200

            # GET historial (debe tener 2 entradas, [0] = más reciente)
            res = await client.get(
                f"/v1/empresas/{empresa_id}/activos/{activo_id}/historial-estados",
                headers=auth,
            )
            assert res.status_code == 200
            logs = res.json()["data"]
            assert len(logs) >= 2
            # El log más reciente debe tener estado_nuevo = en_mantenimiento
            assert logs[0]["attributes"]["estado_nuevo"] == "en_mantenimiento"
            assert logs[0]["attributes"]["estado_anterior"] == "operativo"

    finally:
        app.dependency_overrides.clear()
