"""Test E2E para verificar el CRUD de Planes de Suscripción (SubscriptionPlan).

Endpoint plataforma: /v1/planes — sin empresa_id, requiere autenticación.
"""

from decimal import Decimal
import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.presentation.api.v1.endpoints.dependencies import rate_limit_by_email


@pytest.mark.asyncio
async def test_subscription_plans_crud_and_validation_flow() -> None:
    """Test E2E para verificar CRUD y validaciones de SubscriptionPlan."""
    app.dependency_overrides[rate_limit_by_email] = lambda: None

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            headers = {
                "Content-Type": "application/vnd.api+json",
                "Accept": "application/vnd.api+json",
            }

            # =====================================================================
            # CONFIGURACIÓN: Registrar usuario admin
            # =====================================================================
            tag = uuid.uuid4().hex[:8]
            email = f"admin_{tag}@example.com"
            password = "Password123!"
            reg = await client.post("/v1/auth/registrar", json={
                "data": {"type": "users", "attributes": {
                    "email": email, "password": password, "nombre": "Admin",
                    "company_name": f"Company {tag}", "telefono": "+1111111111",
                }}
            }, headers=headers)
            assert reg.status_code == 201
            token = reg.json()["data"]["attributes"]["access_token"]
            auth_h = {**headers, "Authorization": f"Bearer {token}"}

            # =====================================================================
            # Paso 1: LISTAR inicialmente (GET)
            # =====================================================================
            res_list = await client.get("/v1/planes?limit=100000", headers=auth_h)
            assert res_list.status_code == 200
            initial_count = res_list.json()["meta"]["total"]

            # =====================================================================
            # Paso 2: CREAR plan (POST) — nombre único por tag porque la
            # plataforma no tiene tenant; no debe haber colisiones.
            # =====================================================================
            plan_a_name = f"Premium_{tag}"
            res_create = await client.post("/v1/planes", json={
                "data": {
                    "type": "subscription_plans",
                    "attributes": {
                        "nombre": plan_a_name,
                        "descripcion": "Plan premium con todos los beneficios",
                        "precio_mensual_usd": "99.99",
                        "max_activos": 100,
                        "max_usuarios": 25,
                    },
                }
            }, headers=auth_h)
            assert res_create.status_code == 201, f"Crear Premium: {res_create.text}"
            data_c = res_create.json()["data"]
            plan_id = data_c["id"]
            attrs = data_c["attributes"]
            assert attrs["nombre"] == plan_a_name
            assert attrs["descripcion"] == "Plan premium con todos los beneficios"
            assert Decimal(attrs["precio_mensual_usd"]) == Decimal("99.99")
            assert attrs["max_activos"] == 100
            assert attrs["max_usuarios"] == 25
            assert attrs["is_active"] is True

            # =====================================================================
            # Paso 3: OBTENER plan por ID (GET)
            # =====================================================================
            res_get = await client.get(f"/v1/planes/{plan_id}", headers=auth_h)
            assert res_get.status_code == 200
            assert res_get.json()["data"]["id"] == plan_id

            # =====================================================================
            # Paso 4: CREAR plan Basic (segundo plan)
            # =====================================================================
            res_basic = await client.post("/v1/planes", json={
                "data": {
                    "type": "subscription_plans",
                    "attributes": {
                        "nombre": f"Basic {tag}",
                        "precio_mensual_usd": "29.99",
                        "max_activos": 10,
                        "max_usuarios": 3,
                    },
                }
            }, headers=auth_h)
            assert res_basic.status_code == 201, f"Crear Basic: {res_basic.text}"
            basic_id = res_basic.json()["data"]["id"]

            # =====================================================================
            # Paso 5: LISTAR con 2 planes
            # =====================================================================
            res_list2 = await client.get("/v1/planes?limit=100000", headers=auth_h)
            assert res_list2.status_code == 200
            assert res_list2.json()["meta"]["total"] == initial_count + 2
            ids = [i["id"] for i in res_list2.json()["data"]]
            assert plan_id in ids
            assert basic_id in ids

            # =====================================================================
            # Paso 6: ACTUALIZAR plan (PATCH)
            # =====================================================================
            res_update = await client.patch(f"/v1/planes/{plan_id}", json={
                "data": {
                    "type": "subscription_plans",
                    "attributes": {
                        "nombre": f"Premium Plus {tag}",
                        "precio_mensual_usd": "149.99",
                        "max_activos": 500,
                        "is_active": False,
                    },
                }
            }, headers=auth_h)
            assert res_update.status_code == 200, f"PATCH: {res_update.text}"
            upd = res_update.json()["data"]["attributes"]
            assert upd["nombre"] == f"Premium Plus {tag}"
            assert Decimal(upd["precio_mensual_usd"]) == Decimal("149.99")
            assert upd["max_activos"] == 500
            assert upd["max_usuarios"] == 25  # unchanged from create
            assert upd["is_active"] is False

            # =====================================================================
            # Paso 7: Validar nombre vacío → 422
            # =====================================================================
            res_empty = await client.post("/v1/planes", json={
                "data": {
                    "type": "subscription_plans",
                    "attributes": {
                        "nombre": "",
                        "precio_mensual_usd": "10.00",
                    },
                }
            }, headers=auth_h)
            assert res_empty.status_code == 422
            assert "ERR_SUBSCRIPTION_PLAN_INVALID_DATA" in res_empty.text

            # =====================================================================
            # Paso 8: Validar precio negativo → 422
            # =====================================================================
            res_neg = await client.post("/v1/planes", json={
                "data": {
                    "type": "subscription_plans",
                    "attributes": {
                        "nombre": f"Plan Negativo {tag}",
                        "precio_mensual_usd": "-5.00",
                    },
                }
            }, headers=auth_h)
            assert res_neg.status_code == 422
            assert "ERR_SUBSCRIPTION_PLAN_INVALID_DATA" in res_neg.text

            # =====================================================================
            # Paso 9: Validar nombre duplicado → 409
            # =====================================================================
            res_dup = await client.post("/v1/planes", json={
                "data": {
                    "type": "subscription_plans",
                    "attributes": {
                        "nombre": f"Premium Plus {tag}",
                        "precio_mensual_usd": "199.99",
                    },
                }
            }, headers=auth_h)
            assert res_dup.status_code == 409
            assert "ERR_SUBSCRIPTION_PLAN_ALREADY_EXISTS" in res_dup.text

            # =====================================================================
            # Paso 9.5: SEGURIDAD — Usuario no privilegiado (HTTP 403)
            # =====================================================================
            res_me = await client.get("/v1/auth/yo", headers=auth_h)
            empresa_id = res_me.json()["data"]["attributes"]["empresa_id"]

            user_payload = {
                "data": {
                    "type": "users",
                    "attributes": {
                        "email": f"user_{tag}@example.com",
                        "password": "Password123!",
                        "nombre": "User Normal",
                        "telefono": "+1111111112"
                    }
                }
            }
            res_user = await client.post(
                f"/v1/empresas/{empresa_id}/usuarios",
                json=user_payload,
                headers=auth_h,
            )
            assert res_user.status_code == 201

            res_login = await client.post("/v1/auth/ingresar", json={
                "data": {
                    "type": "tokens",
                    "attributes": {
                        "email": f"user_{tag}@example.com",
                        "password": "Password123!"
                    }
                }
            }, headers=headers)
            assert res_login.status_code == 200
            token_user = res_login.json()["data"]["attributes"]["access_token"]
            auth_h_user = {**headers, "Authorization": f"Bearer {token_user}"}

            # Listar (GET /) -> 403 (solo admin de plataforma)
            res_list_allowed = await client.get("/v1/planes?limit=100000", headers=auth_h_user)
            assert res_list_allowed.status_code == 403

            # Obtener detalle (GET /{id}) -> 403 (solo admin de plataforma)
            res_get_allowed = await client.get(f"/v1/planes/{plan_id}", headers=auth_h_user)
            assert res_get_allowed.status_code == 403

            # Intentar crear (POST /) -> 403 (solo admin)
            res_create_forbidden = await client.post("/v1/planes", json={
                "data": {
                    "type": "subscription_plans",
                    "attributes": {
                        "nombre": "Plan Prohibido",
                        "precio_mensual_usd": "50.00"
                    }
                }
            }, headers=auth_h_user)
            assert res_create_forbidden.status_code == 403

            # Intentar actualizar (PATCH /{id}) -> 403 (solo admin)
            res_patch_forbidden = await client.patch(f"/v1/planes/{plan_id}", json={
                "data": {
                    "type": "subscription_plans",
                    "attributes": {
                        "nombre": "Nombre Prohibido"
                    }
                }
            }, headers=auth_h_user)
            assert res_patch_forbidden.status_code == 403

            # Intentar borrar (DELETE /{id}) -> 403 (solo admin)
            res_delete_forbidden = await client.delete(f"/v1/planes/{plan_id}", headers=auth_h_user)
            assert res_delete_forbidden.status_code == 403

            # =====================================================================
            # Paso 10: ELIMINAR plan (DELETE)
            # =====================================================================
            res_del = await client.delete(f"/v1/planes/{basic_id}", headers=auth_h)
            assert res_del.status_code == 204

            # =====================================================================
            # Paso 11: VERIFICAR eliminación
            # =====================================================================
            res_gone = await client.get(f"/v1/planes/{basic_id}", headers=auth_h)
            assert res_gone.status_code == 404
            assert "ERR_SUBSCRIPTION_PLAN_NOT_FOUND" in res_gone.text

            # =====================================================================
            # Paso 12: ELIMINAR plan inexistente → 404
            # =====================================================================
            fake_id = "00000000-0000-0000-0000-000000000000"
            res_fake = await client.delete(f"/v1/planes/{fake_id}", headers=auth_h)
            assert res_fake.status_code == 404
            assert "ERR_SUBSCRIPTION_PLAN_NOT_FOUND" in res_fake.text

    finally:
        app.dependency_overrides.clear()
