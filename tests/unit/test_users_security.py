"""Tests de seguridad para los endpoints del módulo User.

Verifica que cada endpoint aplique correctamente las dependencias de
autenticación/autorización (require_permission, require_tenant_read)
y que los parámetros de path usen los nombres canónicos definidos
en AGENTS.md para evitar ambigüedad y riesgos IDOR.
"""

import inspect
from collections.abc import Callable
from typing import Any
from unittest.mock import AsyncMock

import pytest

from app.domain.enums import PermissionModule
from app.presentation.api.v1.endpoints.users import (
    create_user,
    delete_user,
    get_user,
    list_users,
    update_user,
)

# ==============================================================================
# UTILIDADES
# ==============================================================================


def _get_dependency(func: Callable[..., Any], param_name: str) -> Any:
    """Extrae la función de dependencia de un parámetro de un endpoint FastAPI."""
    sig = inspect.signature(func)
    param = sig.parameters[param_name]
    default = param.default
    if hasattr(default, "dependency"):
        return default.dependency
    return None


def _get_require_permission_closure_args(func: Callable[..., Any]) -> tuple[Any, ...]:
    """Inspecciona los argumentos de cierre de require_permission en un endpoint.

    Retorna (module, action) extraídos de las variables libres del closure.
    """
    dep = _get_dependency(func, "current_user")
    if dep is None:
        return ()
    closure = getattr(dep, "__closure__", None)
    if not closure:
        return ()
    # Las variables libres son: action, auth_service, auth_use_case, module, token
    # El orden depende del closure, usamos __code__.co_freevars
    free_vars = dep.__code__.co_freevars
    cell_values = {name: cell.cell_contents for name, cell in zip(free_vars, closure, strict=False)}
    return (
        cell_values.get("module"),
        cell_values.get("action"),
    )


# ==============================================================================
# TESTS: Parámetros de path canónicos (anti-IDOR)
# ==============================================================================


class TestUserEndpointPathParams:
    """Verifica que los parámetros de path usen los nombres canónicos del proyecto."""

    def test_list_users_tiene_empresa_id(self) -> None:
        """GET / debe recibir empresa_id (aislamiento de tenant)."""
        sig = inspect.signature(list_users)
        assert "empresa_id" in sig.parameters

    def test_create_user_tiene_empresa_id(self) -> None:
        """POST / debe recibir empresa_id para asociar el usuario al tenant."""
        sig = inspect.signature(create_user)
        assert "empresa_id" in sig.parameters

    def test_get_user_tiene_empresa_id_y_usuario_id(self) -> None:
        """GET /{usuario_id} debe recibir empresa_id y usuario_id (no genérico 'id')."""
        sig = inspect.signature(get_user)
        assert "empresa_id" in sig.parameters
        assert "usuario_id" in sig.parameters

    def test_update_user_tiene_empresa_id_y_usuario_id(self) -> None:
        """PATCH /{usuario_id} debe recibir empresa_id y usuario_id."""
        sig = inspect.signature(update_user)
        assert "empresa_id" in sig.parameters
        assert "usuario_id" in sig.parameters

    def test_delete_user_tiene_empresa_id_y_usuario_id(self) -> None:
        """DELETE /{usuario_id} debe recibir empresa_id y usuario_id."""
        sig = inspect.signature(delete_user)
        assert "empresa_id" in sig.parameters
        assert "usuario_id" in sig.parameters

    def test_endpoints_no_usan_param_id_generico(self) -> None:
        """Ningún endpoint debe usar el parámetro genérico 'id' (propensa a IDOR)."""
        for endpoint in (list_users, create_user, get_user, update_user, delete_user):
            sig = inspect.signature(endpoint)
            assert "id" not in sig.parameters, (
                f"El endpoint '{endpoint.__name__}' usa el parámetro genérico 'id' "
                "en lugar de un nombre específico de entidad."
            )


# ==============================================================================
# TESTS: Dependencias de autenticación (require_permission)
# ==============================================================================


class TestUserEndpointAuthDependencies:
    """Verifica que cada endpoint usa la dependencia de autenticación correcta."""

    def test_list_users_usa_require_permission(self) -> None:
        """GET / debe requerir autenticación (no es endpoint público)."""
        dep = _get_dependency(list_users, "current_user")
        assert dep is not None, "list_users debe tener una dependencia de autenticación"
        assert callable(dep)

    def test_create_user_usa_require_permission(self) -> None:
        """POST / debe requerir autenticación y RBAC."""
        dep = _get_dependency(create_user, "current_user")
        assert dep is not None
        assert callable(dep)

    def test_get_user_usa_require_permission(self) -> None:
        """GET /{usuario_id} debe requerir autenticación."""
        dep = _get_dependency(get_user, "current_user")
        assert dep is not None
        assert callable(dep)

    def test_update_user_usa_require_permission(self) -> None:
        """PATCH /{usuario_id} debe requerir autenticación y RBAC."""
        dep = _get_dependency(update_user, "current_user")
        assert dep is not None
        assert callable(dep)

    def test_delete_user_usa_require_permission(self) -> None:
        """DELETE /{usuario_id} debe requerir autenticación y RBAC."""
        dep = _get_dependency(delete_user, "current_user")
        assert dep is not None
        assert callable(dep)


# ==============================================================================
# TESTS: Módulo y acciones RBAC correctas
# ==============================================================================


class TestUserEndpointRbacConfig:
    """Verifica que los endpoints usan el módulo ADMIN y las acciones RBAC correctas."""

    def test_list_users_usa_modulo_admin_view(self) -> None:
        """GET / debe requerir permiso admin:view."""
        module, action = _get_require_permission_closure_args(list_users)
        assert module == PermissionModule.ADMIN
        assert action == "view"

    def test_create_user_usa_modulo_admin_create(self) -> None:
        """POST / debe requerir permiso admin:create."""
        module, action = _get_require_permission_closure_args(create_user)
        assert module == PermissionModule.ADMIN
        assert action == "create"

    def test_get_user_usa_modulo_admin_view(self) -> None:
        """GET /{usuario_id} debe requerir permiso admin:view."""
        module, action = _get_require_permission_closure_args(get_user)
        assert module == PermissionModule.ADMIN
        assert action == "view"

    def test_update_user_usa_modulo_admin_edit(self) -> None:
        """PATCH /{usuario_id} debe requerir permiso admin:edit."""
        module, action = _get_require_permission_closure_args(update_user)
        assert module == PermissionModule.ADMIN
        assert action == "edit"

    def test_delete_user_usa_modulo_admin_delete(self) -> None:
        """DELETE /{usuario_id} debe requerir permiso admin:delete."""
        module, action = _get_require_permission_closure_args(delete_user)
        assert module == PermissionModule.ADMIN
        assert action == "delete"


# ==============================================================================
# TESTS: Comportamiento del endpoint (sin base de datos)
# ==============================================================================


class TestUserEndpointBehavior:
    """Verifica el comportamiento funcional de los endpoints con mocks."""

    @pytest.mark.asyncio
    async def test_list_users_retorna_documento_jsonapi(self) -> None:
        """GET / debe retornar un UserListDocument con la lista de usuarios."""
        from datetime import UTC, datetime

        from app.application.dtos.user_dtos import UserResponse

        mock_user = UserResponse(
            id="22222222-2222-2222-2222-222222222222",
            email="test@gema.com",
            nombre="Test User",
            empresa_id="11111111-1111-1111-1111-111111111111",
            telefono=None,
            activo=True,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        current_user_mock = type("CurrentUser", (), {"empresa_id": "11111111-1111-1111-1111-111111111111"})()
        use_case_mock = AsyncMock()
        use_case_mock.execute = AsyncMock(return_value=[mock_user])

        result = await list_users(
            empresa_id="11111111-1111-1111-1111-111111111111",
            current_user=current_user_mock,
            use_case=use_case_mock,
        )

        use_case_mock.execute.assert_called_once_with("11111111-1111-1111-1111-111111111111")
        assert result is not None
        assert len(result.data) == 1
        assert result.meta["total"] == 1

    @pytest.mark.asyncio
    async def test_create_user_pasa_empresa_id_al_use_case(self) -> None:
        """POST / debe pasar empresa_id y el DTO al use case correctamente."""
        from datetime import UTC, datetime

        from app.application.dtos.user_dtos import UserResponse
        from app.presentation.api.v1.schemas.user import (
            CreateUserRequest as CreateUserSchema,
        )

        mock_response = UserResponse(
            id="22222222-2222-2222-2222-222222222222",
            email="nuevo@gema.com",
            nombre="Nuevo Usuario",
            empresa_id="11111111-1111-1111-1111-111111111111",
            telefono=None,
            activo=True,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        current_user_mock = type("CurrentUser", (), {"empresa_id": "11111111-1111-1111-1111-111111111111"})()
        use_case_mock = AsyncMock()
        use_case_mock.execute = AsyncMock(return_value=mock_response)

        # Construir la request JSON:API
        request_data = CreateUserSchema.model_validate({
            "data": {
                "type": "usuarios",
                "attributes": {
                    "email": "nuevo@gema.com",
                    "password": "ClaveSegura123!",
                    "nombre": "Nuevo Usuario",
                },
            }
        })

        result = await create_user(
            empresa_id="11111111-1111-1111-1111-111111111111",
            request=request_data,
            current_user=current_user_mock,
            use_case=use_case_mock,
        )

        # Verificar que el use case fue llamado con empresa_id y el DTO
        assert use_case_mock.execute.called
        call_args = use_case_mock.execute.call_args
        # El endpoint llama: use_case.execute(empresa_id, dto) → args posicionales
        assert call_args[0][0] == "11111111-1111-1111-1111-111111111111"
        assert result is not None
        assert result.data.attributes.email == "nuevo@gema.com"

    @pytest.mark.asyncio
    async def test_delete_user_baja_logica_retorna_204(self) -> None:
        """DELETE /{usuario_id} debe retornar None y llamar al use case."""
        from datetime import UTC, datetime

        from app.application.dtos.user_dtos import UserResponse

        mock_response = UserResponse(
            id="22222222-2222-2222-2222-222222222222",
            email="borrar@gema.com",
            nombre="A Borrar",
            empresa_id="11111111-1111-1111-1111-111111111111",
            telefono=None,
            activo=False,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        current_user_mock = type("CurrentUser", (), {"empresa_id": "11111111-1111-1111-1111-111111111111"})()
        use_case_mock = AsyncMock()
        use_case_mock.execute = AsyncMock(return_value=mock_response)

        result = await delete_user(
            empresa_id="11111111-1111-1111-1111-111111111111",
            usuario_id="22222222-2222-2222-2222-222222222222",
            current_user=current_user_mock,
            use_case=use_case_mock,
        )

        use_case_mock.execute.assert_called_once_with(
            "22222222-2222-2222-2222-222222222222"
        )
        assert result is None
