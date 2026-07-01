import uuid
from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.composition.container.common import get_notification_sender
from app.main import app
from app.presentation.api.v1.endpoints.dependencies import rate_limit_by_email


@pytest.mark.asyncio
async def test_complete_auth_flow():
    """Test e2e completo del flujo de autenticación.

    Cubre registro, login, obtención de perfil actual, rotación de tokens,
    cambio de contraseña, recuperación de contraseña por token y cierre de sesión.
    """
    # 1. Mockear el rate limit para evitar bloqueos por email
    app.dependency_overrides[rate_limit_by_email] = lambda: None

    # 2. Mockear el notification sender para interceptar el token de recuperación
    mock_notification = AsyncMock()
    app.dependency_overrides[get_notification_sender] = lambda: mock_notification

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            unique_id = uuid.uuid4().hex[:8]
            email = f"auth_flow_test_{unique_id}@example.com"
            password = "Password123!"
            new_password = "NewPassword123!"
            reset_password = "ResetPassword123!"
            company_name = f"Empresa Test Auth {unique_id}"
            headers = {
                "Content-Type": "application/vnd.api+json",
                "Accept": "application/vnd.api+json",
            }

            # =====================================================================
            # Paso 1: Registrar usuario
            # =====================================================================
            register_payload = {
                "data": {
                    "type": "users",
                    "attributes": {
                        "email": email,
                        "password": password,
                        "nombre": "User Test Auth",
                        "company_name": company_name,
                        "telefono": "+584120000000",
                    },
                }
            }
            res_reg = await client.post("/v1/auth/registrar", json=register_payload, headers=headers)
            assert res_reg.status_code == 201, f"Registro fallido: {res_reg.text}"
            tokens = res_reg.json()["data"]["attributes"]
            assert "access_token" in tokens
            assert "refresh_token" in tokens
            access_token = tokens["access_token"]

            # =====================================================================
            # Paso 2: Obtener perfil de usuario actual (/v1/auth/yo)
            # =====================================================================
            auth_headers = {**headers, "Authorization": f"Bearer {access_token}"}
            res_me = await client.get("/v1/auth/yo", headers=auth_headers)
            assert res_me.status_code == 200, f"Error al obtener perfil actual: {res_me.text}"
            me_attributes = res_me.json()["data"]["attributes"]
            assert me_attributes["email"] == email
            assert me_attributes["nombre"] == "User Test Auth"
            assert "empresa_id" in me_attributes

            # =====================================================================
            # Paso 3: Iniciar sesión (Login)
            # =====================================================================
            login_payload = {
                "data": {
                    "type": "tokens",
                    "attributes": {
                        "email": email,
                        "password": password,
                    },
                }
            }
            res_login = await client.post("/v1/auth/ingresar", json=login_payload, headers=headers)
            assert res_login.status_code == 200, f"Login fallido: {res_login.text}"
            tokens_login = res_login.json()["data"]["attributes"]
            assert "access_token" in tokens_login
            assert "refresh_token" in tokens_login
            refresh_token_login = tokens_login["refresh_token"]

            # =====================================================================
            # Paso 4: Login fallido con contraseña incorrecta
            # =====================================================================
            invalid_login_payload = {
                "data": {
                    "type": "tokens",
                    "attributes": {
                        "email": email,
                        "password": "WrongPassword!",
                    },
                }
            }
            res_invalid_login = await client.post(
                "/v1/auth/ingresar", json=invalid_login_payload, headers=headers
            )
            assert res_invalid_login.status_code == 401

            # =====================================================================
            # Paso 5: Rotar tokens de autenticación (/v1/auth/refrescar)
            # =====================================================================
            refresh_payload = {
                "data": {
                    "type": "tokens",
                    "attributes": {
                        "refresh_token": refresh_token_login,
                    },
                }
            }
            res_refresh = await client.post("/v1/auth/refrescar", json=refresh_payload, headers=headers)
            assert res_refresh.status_code == 200, f"Rotación fallida: {res_refresh.text}"
            tokens_refreshed = res_refresh.json()["data"]["attributes"]
            assert "access_token" in tokens_refreshed
            assert "refresh_token" in tokens_refreshed
            access_token_new = tokens_refreshed["access_token"]

            # =====================================================================
            # Paso 6: Cambiar contraseña (/v1/auth/cambiar-contrasena)
            # =====================================================================
            change_headers = {**headers, "Authorization": f"Bearer {access_token_new}"}
            change_payload = {
                "data": {
                    "type": "passwords",
                    "attributes": {
                        "old_password": password,
                        "new_password": new_password,
                    },
                }
            }
            res_change = await client.post(
                "/v1/auth/cambiar-contrasena", json=change_payload, headers=change_headers
            )
            assert res_change.status_code == 200, f"Cambio de contraseña fallido: {res_change.text}"

            # Verificar que login con contraseña vieja ahora falla
            res_old_login = await client.post("/v1/auth/ingresar", json=login_payload, headers=headers)
            assert res_old_login.status_code == 401

            # Verificar que login con contraseña nueva funciona
            login_payload_new = {
                "data": {
                    "type": "tokens",
                    "attributes": {
                        "email": email,
                        "password": new_password,
                    },
                }
            }
            res_new_login = await client.post(
                "/v1/auth/ingresar", json=login_payload_new, headers=headers
            )
            assert res_new_login.status_code == 200

            # =====================================================================
            # Paso 7: Solicitar reset de contraseña (/v1/auth/olvide-contrasena)
            # =====================================================================
            forgot_payload = {
                "data": {
                    "type": "passwords",
                    "attributes": {
                        "email": email,
                    },
                }
            }
            res_forgot = await client.post(
                "/v1/auth/olvide-contrasena", json=forgot_payload, headers=headers
            )
            assert res_forgot.status_code == 202, f"Solicitud de reset fallida: {res_forgot.text}"

            # Verificar que mock_notification.send_password_reset fue llamado
            assert mock_notification.send_password_reset.called
            # Obtener el raw_token del argumento reset_url
            called_args = mock_notification.send_password_reset.call_args[1]
            reset_url = called_args["reset_url"]
            # reset_url es http://localhost:3000/reset-password?token=xxxx
            raw_token = reset_url.split("token=")[1]

            # =====================================================================
            # Paso 8: Restablecer contraseña con token (/v1/auth/restablecer-contrasena)
            # =====================================================================
            reset_payload = {
                "data": {
                    "type": "passwords",
                    "attributes": {
                        "token": raw_token,
                        "new_password": reset_password,
                    },
                }
            }
            res_reset = await client.post(
                "/v1/auth/restablecer-contrasena", json=reset_payload, headers=headers
            )
            assert res_reset.status_code == 200, f"Reset de contraseña fallido: {res_reset.text}"

            # Verificar que login con contraseña restablecida funciona
            login_payload_reset = {
                "data": {
                    "type": "tokens",
                    "attributes": {
                        "email": email,
                        "password": reset_password,
                    },
                }
            }
            res_reset_login = await client.post(
                "/v1/auth/ingresar", json=login_payload_reset, headers=headers
            )
            assert res_reset_login.status_code == 200
            access_token_reset = res_reset_login.json()["data"]["attributes"]["access_token"]
            refresh_token_reset = res_reset_login.json()["data"]["attributes"]["refresh_token"]

            # =====================================================================
            # Paso 9: Cerrar sesión (/v1/auth/cerrar-sesion)
            # =====================================================================
            logout_headers = {**headers, "Authorization": f"Bearer {access_token_reset}"}
            logout_payload = {
                "data": {
                    "type": "tokens",
                    "attributes": {
                        "access_token": access_token_reset,
                        "refresh_token": refresh_token_reset,
                    },
                }
            }
            res_logout = await client.post(
                "/v1/auth/cerrar-sesion", json=logout_payload, headers=logout_headers
            )
            assert res_logout.status_code == 204

            # Verificar que acceder a /yo con el token cerrado ahora falla
            res_me_revoked = await client.get("/v1/auth/yo", headers=logout_headers)
            assert res_me_revoked.status_code == 401

    finally:
        app.dependency_overrides.clear()
