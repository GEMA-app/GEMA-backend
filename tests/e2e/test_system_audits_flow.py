"""Test E2E para verificar el listado, filtrado y aislamiento multi-tenant de las Auditorías de Sistema."""

import uuid
from datetime import datetime, timezone
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.presentation.api.v1.endpoints.dependencies import rate_limit_by_email
from app.infrastructure.db.session import async_session_factory
from app.infrastructure.db.models.system_audits import SystemAuditModel


@pytest.mark.asyncio
async def test_system_audits_crud_and_isolation_flow() -> None:
    """Test E2E para verificar la correcta consulta y seguridad de las auditorías de sistema."""
    app.dependency_overrides[rate_limit_by_email] = lambda: None

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            headers = {
                "Content-Type": "application/vnd.api+json",
                "Accept": "application/vnd.api+json",
            }

            # =====================================================================
            # CONFIG: Registrar Compañía A y Compañía B
            # =====================================================================
            tag_a = uuid.uuid4().hex[:8]
            email_a = f"admin_a_{tag_a}@example.com"
            company_a_name = f"Company A {tag_a}"
            password = "Password123!"

            reg_payload_a = {
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
            res_reg_a = await client.post("/v1/auth/registrar", json=reg_payload_a, headers=headers)
            assert res_reg_a.status_code == 201
            token_a = res_reg_a.json()["data"]["attributes"]["access_token"]
            auth_h_a = {**headers, "Authorization": f"Bearer {token_a}"}

            res_me_a = await client.get("/v1/auth/yo", headers=auth_h_a)
            empresa_a_id = res_me_a.json()["data"]["attributes"]["empresa_id"]
            admin_a_id = res_me_a.json()["data"]["id"]

            # Registrar Compañía B
            tag_b = uuid.uuid4().hex[:8]
            email_b = f"admin_b_{tag_b}@example.com"
            company_b_name = f"Company B {tag_b}"

            reg_payload_b = {
                "data": {
                    "type": "users",
                    "attributes": {
                        "email": email_b,
                        "password": password,
                        "nombre": "Admin B",
                        "company_name": company_b_name,
                        "telefono": "+2222222222",
                    },
                }
            }
            res_reg_b = await client.post("/v1/auth/registrar", json=reg_payload_b, headers=headers)
            assert res_reg_b.status_code == 201
            token_b = res_reg_b.json()["data"]["attributes"]["access_token"]
            auth_h_b = {**headers, "Authorization": f"Bearer {token_b}"}

            res_me_b = await client.get("/v1/auth/yo", headers=auth_h_b)
            empresa_b_id = res_me_b.json()["data"]["attributes"]["empresa_id"]
            admin_b_id = res_me_b.json()["data"]["id"]

            # =====================================================================
            # CONFIG: Insertar registros de auditoría de prueba en la base de datos
            # =====================================================================
            audit_a1_id = uuid.uuid4()
            audit_a2_id = uuid.uuid4()
            audit_a3_id = uuid.uuid4()
            audit_b1_id = uuid.uuid4()

            async with async_session_factory() as session:
                # Audit 1 (Company A)
                audit_a1 = SystemAuditModel(
                    id=audit_a1_id,
                    empresa_id=uuid.UUID(empresa_a_id),
                    usuario_id=uuid.UUID(admin_a_id),
                    accion="user.login",
                    detalles={"description": "Admin logged in"},
                    ip_address="127.0.0.1",
                    ocurrido_en=datetime.now(timezone.utc),
                )
                # Audit 2 (Company A)
                audit_a2 = SystemAuditModel(
                    id=audit_a2_id,
                    empresa_id=uuid.UUID(empresa_a_id),
                    usuario_id=uuid.UUID(admin_a_id),
                    accion="asset.create",
                    detalles={"asset_name": "Bomba-101"},
                    ip_address="192.168.1.10",
                    ocurrido_en=datetime.now(timezone.utc),
                )
                # Audit 3 (Company A, without user_id)
                audit_a3 = SystemAuditModel(
                    id=audit_a3_id,
                    empresa_id=uuid.UUID(empresa_a_id),
                    usuario_id=None,
                    accion="system.background_job",
                    detalles={"job": "cleanup"},
                    ip_address=None,
                    ocurrido_en=datetime.now(timezone.utc),
                )
                # Audit 4 (Company B)
                audit_b1 = SystemAuditModel(
                    id=audit_b1_id,
                    empresa_id=uuid.UUID(empresa_b_id),
                    usuario_id=uuid.UUID(admin_b_id),
                    accion="user.login",
                    detalles={"description": "Admin B logged in"},
                    ip_address="10.0.0.1",
                    ocurrido_en=datetime.now(timezone.utc),
                )

                session.add_all([audit_a1, audit_a2, audit_a3, audit_b1])
                await session.commit()

            # =====================================================================
            # Paso 1: LISTAR auditorías de la Compañía A (GET)
            # =====================================================================
            res_list = await client.get(
                f"/v1/empresas/{empresa_a_id}/auditorias",
                headers=auth_h_a,
            )
            assert res_list.status_code == 200
            data_list = res_list.json()["data"]
            assert len(data_list) == 3
            assert res_list.json()["meta"]["total"] == 3

            # =====================================================================
            # Paso 2: FILTRAR por Acción (GET)
            # =====================================================================
            res_filter_action = await client.get(
                f"/v1/empresas/{empresa_a_id}/auditorias?accion=user.login",
                headers=auth_h_a,
            )
            assert res_filter_action.status_code == 200
            data_filter_action = res_filter_action.json()["data"]
            assert len(data_filter_action) == 1
            assert data_filter_action[0]["id"] == str(audit_a1_id)

            # =====================================================================
            # Paso 3: FILTRAR por Usuario (GET)
            # =====================================================================
            res_filter_user = await client.get(
                f"/v1/empresas/{empresa_a_id}/auditorias?usuario_id={admin_a_id}",
                headers=auth_h_a,
            )
            assert res_filter_user.status_code == 200
            data_filter_user = res_filter_user.json()["data"]
            assert len(data_filter_user) == 2
            ids = [x["id"] for x in data_filter_user]
            assert str(audit_a1_id) in ids
            assert str(audit_a2_id) in ids

            # =====================================================================
            # Paso 4: OBTENER auditoría por ID (GET)
            # =====================================================================
            res_get = await client.get(
                f"/v1/empresas/{empresa_a_id}/auditorias/{audit_a2_id}",
                headers=auth_h_a,
            )
            assert res_get.status_code == 200
            attrs = res_get.json()["data"]["attributes"]
            assert attrs["accion"] == "asset.create"
            assert attrs["detalles"]["asset_name"] == "Bomba-101"
            assert attrs["ip_address"] == "192.168.1.10"

            # =====================================================================
            # Paso 5: SEGURIDAD — Aislamiento multi-tenant (HTTP 403)
            # =====================================================================
            # Compañía B no debe listar auditorías de Compañía A
            res_list_forbidden = await client.get(
                f"/v1/empresas/{empresa_a_id}/auditorias",
                headers=auth_h_b,
            )
            assert res_list_forbidden.status_code == 403

            # Compañía B no debe obtener detalle de auditoría de Compañía A
            res_get_forbidden = await client.get(
                f"/v1/empresas/{empresa_a_id}/auditorias/{audit_a1_id}",
                headers=auth_h_b,
            )
            assert res_get_forbidden.status_code == 403

            # =====================================================================
            # Paso 6: Obtener auditoría inexistente -> 404
            # =====================================================================
            fake_id = uuid.uuid4()
            res_fake = await client.get(
                f"/v1/empresas/{empresa_a_id}/auditorias/{fake_id}",
                headers=auth_h_a,
            )
            assert res_fake.status_code == 404
            assert "ERR_SYSTEM_AUDIT_NOT_FOUND" in res_fake.text

    finally:
        app.dependency_overrides.clear()
