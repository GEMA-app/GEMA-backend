"""Test E2E para CRUD, transacciones de movimientos, aislamiento multi-tenant y bloqueos en Inventario."""

import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.infrastructure.config.settings import settings
from app.infrastructure.db.models.supplier import SupplierModel
from app.main import app
from app.presentation.api.v1.endpoints.dependencies import rate_limit_by_email


@pytest.mark.asyncio
async def test_inventory_crud_movements_and_isolation_flow():
    """Test E2E para verificar todo el ciclo de vida del inventario y movimientos."""
    app.dependency_overrides[rate_limit_by_email] = lambda: None

    engine = create_async_engine(settings.DATABASE_URL, poolclass=NullPool)
    db_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

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
            assert res.status_code == 201, f"Registro A fallo: {res.text}"
            tokens = res.json()["data"]["attributes"]
            access_token = tokens["access_token"]
            auth_headers = {**headers, "Authorization": f"Bearer {access_token}"}

            res_me = await client.get("/v1/auth/yo", headers=auth_headers)
            me = res_me.json()["data"]
            empresa_id = me["attributes"]["empresa_id"]

            # =================================================================
            # SEED: categoria catalogo → articulo catalogo → proveedor
            # =================================================================
            cat = await client.post(
                f"/v1/empresas/{empresa_id}/catalogo/categorias",
                json={"data": {"type": "article_categories", "attributes": {"name": "Categoria Test"}}},
                headers=auth_headers,
            )
            assert cat.status_code == 201
            category_id = cat.json()["data"]["id"]

            art = await client.post(
                f"/v1/empresas/{empresa_id}/catalogo/articulos",
                json={"data": {"type": "catalog-articles", "attributes": {"category_id": category_id, "name": "Articulo Test"}}},
                headers=auth_headers,
            )
            assert art.status_code == 201
            articulo_id = art.json()["data"]["id"]

            # Insertar un proveedor de prueba en la BD para asociar al repuesto
            async with db_factory() as session:
                supplier = SupplierModel(
                    id=uuid.uuid4(),
                    nombre="Proveedor Test",
                    empresa_id=uuid.UUID(empresa_id),
                )
                session.add(supplier)
                await session.commit()
                supplier_id = str(supplier.id)

            # =================================================================
            # Paso 1: CREAR un repuesto en el inventario con stock inicial (POST /inventario)
            # =================================================================
            create_payload = {
                "data": {
                    "type": "inventory_parts",
                    "attributes": {
                        "articulo_id": articulo_id,
                        "proveedor_id": supplier_id,
                        "stock_actual": 50,
                        "stock_minimo": 10,
                        "ubicacion_almacen": "Almacen Central Estante 4",
                        "precio_unitario": 15.50,
                        "moneda": "USD",
                    }
                }
            }
            res_create = await client.post(
                f"/v1/empresas/{empresa_id}/inventario",
                json=create_payload,
                headers=auth_headers,
            )
            assert res_create.status_code == 201, f"Creacion de repuesto fallo: {res_create.text}"
            repuesto_id = res_create.json()["data"]["id"]
            assert res_create.json()["data"]["attributes"]["stock_actual"] == 50

            # =================================================================
            # Paso 2: OBTENER el repuesto por ID (GET /inventario/{repuesto_id})
            # =================================================================
            res_get = await client.get(
                f"/v1/empresas/{empresa_id}/inventario/{repuesto_id}",
                headers=auth_headers,
            )
            assert res_get.status_code == 200
            assert res_get.json()["data"]["attributes"]["ubicacion_almacen"] == "Almacen Central Estante 4"

            # =================================================================
            # Paso 3: LISTAR repuestos (GET /inventario)
            # =================================================================
            res_list = await client.get(
                f"/v1/empresas/{empresa_id}/inventario",
                headers=auth_headers,
            )
            assert res_list.status_code == 200
            assert len(res_list.json()["data"]) >= 1

            # =================================================================
            # Paso 4: ACTUALIZAR parámetros del repuesto (PATCH /inventario/{repuesto_id})
            # =================================================================
            update_payload = {
                "data": {
                    "type": "inventory_parts",
                    "id": repuesto_id,
                    "attributes": {
                        "stock_minimo": 15,
                        "ubicacion_almacen": "Almacen Central Estante 5"
                    }
                }
            }
            res_patch = await client.patch(
                f"/v1/empresas/{empresa_id}/inventario/{repuesto_id}",
                json=update_payload,
                headers=auth_headers,
            )
            assert res_patch.status_code == 200
            assert res_patch.json()["data"]["attributes"]["stock_minimo"] == 15
            assert res_patch.json()["data"]["attributes"]["ubicacion_almacen"] == "Almacen Central Estante 5"

            # =================================================================
            # Paso 5: REGISTRAR un movimiento de salida (POST /inventario/{id}/movimientos)
            # =================================================================
            movement_payload = {
                "data": {
                    "type": "inventory_entries",
                    "attributes": {
                        "movement_type": "salida",
                        "quantity": 10,
                        "reason": "Consumo de repuesto por mantenimiento correctivo"
                    }
                }
            }
            res_mov = await client.post(
                f"/v1/empresas/{empresa_id}/inventario/{repuesto_id}/movimientos",
                json=movement_payload,
                headers=auth_headers,
            )
            assert res_mov.status_code == 201, f"Registro de movimiento fallo: {res_mov.text}"
            movimiento_id = res_mov.json()["data"]["id"]
            assert res_mov.json()["data"]["attributes"]["quantity"] == 10
            assert res_mov.json()["data"]["attributes"]["movement_type"] == "salida"

            # Verificar que el stock actual del repuesto disminuyó
            res_check = await client.get(
                f"/v1/empresas/{empresa_id}/inventario/{repuesto_id}",
                headers=auth_headers,
            )
            assert res_check.json()["data"]["attributes"]["stock_actual"] == 40  # 50 - 10

            # =================================================================
            # Paso 6: LISTAR movimientos (GET /inventario/{id}/movimientos)
            # =================================================================
            res_movs = await client.get(
                f"/v1/empresas/{empresa_id}/inventario/{repuesto_id}/movimientos",
                headers=auth_headers,
            )
            assert res_movs.status_code == 200, f"Listar movimientos fallo: {res_movs.text}"
            assert len(res_movs.json()["data"]) >= 1
            movs_ids = [m["id"] for m in res_movs.json()["data"]]
            assert movimiento_id in movs_ids

            # =================================================================
            # Paso 7: OBTENER detalle de un movimiento por ID (GET /movimientos/{id})
            # =================================================================
            res_mov_get = await client.get(
                f"/v1/empresas/{empresa_id}/inventario/{repuesto_id}/movimientos/{movimiento_id}",
                headers=auth_headers,
            )
            assert res_mov_get.status_code == 200, f"Obtener movimiento fallo: {res_mov_get.text}"
            assert res_mov_get.json()["data"]["attributes"]["quantity"] == 10

            # =================================================================
            # CONFIG: Registrar Compañía B (Aislamiento Multi-Tenant)
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

            # =================================================================
            # Paso 8: VERIFICAR aislamiento multi-tenant (Forbidden 403)
            # =================================================================
            # Compañía B no puede leer el repuesto de Compañía A
            res_isolation_part = await client.get(
                f"/v1/empresas/{empresa_id}/inventario/{repuesto_id}",
                headers=auth_headers_b,
            )
            assert res_isolation_part.status_code == 403

            # Compañía B no puede leer los movimientos de Compañía A
            res_isolation_mov = await client.get(
                f"/v1/empresas/{empresa_id}/inventario/{repuesto_id}/movimientos",
                headers=auth_headers_b,
            )
            assert res_isolation_mov.status_code == 403

            # =================================================================
            # Paso 9: INTENTAR borrar repuesto con stock > 0 (422)
            # =================================================================
            res_del_fail = await client.delete(
                f"/v1/empresas/{empresa_id}/inventario/{repuesto_id}",
                headers=auth_headers,
            )
            assert res_del_fail.status_code == 422 or res_del_fail.status_code == 409

    finally:
        app.dependency_overrides.clear()
        await engine.dispose()
