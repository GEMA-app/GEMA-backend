"""Test E2E para CRUD y aislamiento multi-tenant de repuestos utilizados (UsedPart)."""

import uuid
from decimal import Decimal

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.infrastructure.config.settings import settings
from app.infrastructure.db.models.inventory_part import InventoryPartModel
from app.infrastructure.db.models.supplier import SupplierModel
from app.main import app
from app.presentation.api.v1.endpoints.dependencies import rate_limit_by_email


@pytest.mark.asyncio
async def test_used_parts_crud_and_isolation_flow():
    """Test E2E para CRUD y aislamiento multi-tenant de repuestos utilizados."""
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
            usuario_id = me["id"]

            # =================================================================
            # SEED: categoria catalogo → articulo catalogo → activo → OT → intervencion
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
            assert wo.status_code == 201, f"Crear OT fallo: {wo.text}"
            ot_id = wo.json()["data"]["id"]

            intervention = await client.post(
                f"/v1/empresas/{empresa_id}/ordenes-trabajo/{ot_id}/intervenciones",
                json={"data": {"type": "intervenciones", "attributes": {"work_order_id": ot_id, "technician_id": usuario_id, "tareas_realizadas": "Inspeccion", "fecha_inicio": "2026-06-28T10:00:00", "horas_hombre": 1.0}}},
                headers=auth_headers,
            )
            assert intervention.status_code == 201, f"Crear intervencion fallo: {intervention.text}"
            intervencion_id = intervention.json()["data"]["id"]

            # =================================================================
            # SEED: Proveedor + Inventario (INSERT directo en BD)
            # =================================================================
            async with db_factory() as session:
                # Proveedor
                supplier_id = uuid.uuid4()
                await session.execute(
                    insert(SupplierModel).values(
                        id=supplier_id,
                        nombre="Proveedor Test",
                        empresa_id=uuid.UUID(empresa_id),
                    )
                )
                # Inventario repuesto
                repuesto_id = uuid.uuid4()
                await session.execute(
                    insert(InventoryPartModel).values(
                        id=repuesto_id,
                        articulo_id=uuid.UUID(articulo_id),
                        proveedor_id=supplier_id,
                        stock_actual=100,
                        stock_minimo=10,
                        precio_unitario=Decimal("50.00"),
                        moneda="USD",
                        empresa_id=uuid.UUID(empresa_id),
                    )
                )
                await session.commit()

            # =================================================================
            # Paso 1: CREAR repuesto utilizado
            # =================================================================
            create_payload = {
                "data": {
                    "type": "repuesto-utilizado",
                    "attributes": {
                        "intervencion_id": intervencion_id,
                        "repuesto_id": str(repuesto_id),
                        "cantidad_usada": 3,
                        "precio_unitario": 50.00,
                        "moneda": "USD",
                    },
                }
            }
            res_create = await client.post(
                f"/v1/empresas/{empresa_id}/ordenes-trabajo/{ot_id}/intervenciones/{intervencion_id}/repuestos-utilizados",
                json=create_payload,
                headers=auth_headers,
            )
            assert res_create.status_code == 201, f"Crear repuesto fallo: {res_create.text}"
            used_id = res_create.json()["data"]["id"]
            attrs = res_create.json()["data"]["attributes"]
            assert attrs["cantidad_usada"] == 3
            assert attrs["moneda"] == "USD"

            # =================================================================
            # Paso 2: OBTENER repuesto utilizado por ID
            # =================================================================
            res_get = await client.get(
                f"/v1/empresas/{empresa_id}/ordenes-trabajo/{ot_id}/intervenciones/{intervencion_id}/repuestos-utilizados/{used_id}",
                headers=auth_headers,
            )
            assert res_get.status_code == 200
            assert res_get.json()["data"]["attributes"]["cantidad_usada"] == 3

            # =================================================================
            # Paso 3: LISTAR repuestos utilizados
            # =================================================================
            res_list = await client.get(
                f"/v1/empresas/{empresa_id}/ordenes-trabajo/{ot_id}/intervenciones/{intervencion_id}/repuestos-utilizados",
                headers=auth_headers,
            )
            assert res_list.status_code == 200
            data = res_list.json()["data"]
            ids = [r["id"] for r in data]
            assert used_id in ids

            # =================================================================
            # Paso 4: ACTUALIZAR cantidad usada
            # =================================================================
            update_payload = {
                "data": {
                    "type": "repuesto-utilizado",
                    "id": used_id,
                    "attributes": {
                        "cantidad_usada": 5,
                    },
                }
            }
            res_update = await client.patch(
                f"/v1/empresas/{empresa_id}/ordenes-trabajo/{ot_id}/intervenciones/{intervencion_id}/repuestos-utilizados/{used_id}",
                json=update_payload,
                headers=auth_headers,
            )
            assert res_update.status_code == 200, f"Actualizar repuesto fallo: {res_update.text}"
            assert res_update.json()["data"]["attributes"]["cantidad_usada"] == 5

            # =================================================================
            # CONFIG: Registrar Compania B
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
            # Paso 5: AISLAMIENTO MULTI-TENANT
            # =================================================================
            # Token B accediendo a ruta de Empresa A → 403
            res_403 = await client.get(
                f"/v1/empresas/{empresa_id}/ordenes-trabajo/{ot_id}/intervenciones/{intervencion_id}/repuestos-utilizados/{used_id}",
                headers=auth_headers_b,
            )
            assert res_403.status_code == 403

            # =================================================================
            # Paso 6: ELIMINAR repuesto utilizado
            # =================================================================
            res_delete = await client.delete(
                f"/v1/empresas/{empresa_id}/ordenes-trabajo/{ot_id}/intervenciones/{intervencion_id}/repuestos-utilizados/{used_id}",
                headers=auth_headers,
            )
            assert res_delete.status_code == 204, f"Eliminar repuesto fallo: {res_delete.text}"

            # Verificar que ya no existe
            res_gone = await client.get(
                f"/v1/empresas/{empresa_id}/ordenes-trabajo/{ot_id}/intervenciones/{intervencion_id}/repuestos-utilizados/{used_id}",
                headers=auth_headers,
            )
            assert res_gone.status_code == 404

    finally:
        app.dependency_overrides.clear()
        await engine.dispose()
