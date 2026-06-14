from typing import Any
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.application.use_cases.role.delete_role import DeleteRoleUseCase
from app.application.use_cases.role.revoke_role import RevokeRoleFromUserUseCase
from app.domain.entities import Permission, Role
from app.domain.enums import PermissionModule
from app.domain.exceptions import LastAdminRevocationError, ValidationException
from app.domain.value_objects import CompanyId, RoleId, UserId


@pytest.fixture
def mock_uow() -> Any:
    uow = MagicMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)
    uow.roles = MagicMock()
    uow.roles.get_by_id = AsyncMock()
    uow.roles.delete = AsyncMock()
    uow.roles.revoke_from_user = AsyncMock()
    uow.roles.count_admin_users = AsyncMock()
    uow.roles.get_user_roles = AsyncMock()
    uow.roles.assign_to_user = AsyncMock()
    uow.roles.save = AsyncMock()
    uow.users = MagicMock()
    uow.users.get_by_id = AsyncMock()
    uow.commit = AsyncMock()
    return uow


class TestDeleteRoleUseCase:

    async def test_delete_role_administrador_raises_validation_exception(self, mock_uow: Any) -> None:
        company_id = CompanyId(uuid4())
        role_id = RoleId(uuid4())

        # Simular un rol con nombre "Administrador"
        role = Role(
            id=role_id,
            empresa_id=company_id,
            nombre="Administrador",
            descripcion="Admin rol",
            permisos=[]
        )
        mock_uow.roles.get_by_id.return_value = role

        use_case = DeleteRoleUseCase(uow=mock_uow)
        with pytest.raises(ValidationException) as exc_info:
            await use_case.execute(str(company_id.value), str(role_id.value))

        assert "No se puede eliminar el rol de Administrador" in str(exc_info.value)

    async def test_delete_last_admin_role_raises_last_admin_revocation_error(self, mock_uow: Any) -> None:
        company_id = CompanyId(uuid4())
        role_id = RoleId(uuid4())

        # Simular un rol con permisos de admin
        perm = Permission(module=PermissionModule.ADMIN, can_delete=True)
        role = Role(
            id=role_id,
            empresa_id=company_id,
            nombre="SuperAdmin",
            descripcion="Admin rol",
            permisos=[perm]
        )
        mock_uow.roles.get_by_id.return_value = role
        # Simular que queda 1 o menos administradores
        mock_uow.roles.count_admin_users.return_value = 1

        use_case = DeleteRoleUseCase(uow=mock_uow)
        with pytest.raises(LastAdminRevocationError):
            await use_case.execute(str(company_id.value), str(role_id.value))

        mock_uow.roles.count_admin_users.assert_called_once_with(empresa_id=company_id)
        mock_uow.roles.delete.assert_not_called()


class TestRevokeRoleFromUserUseCase:

    async def test_revoke_last_admin_role_raises_last_admin_revocation_error(self, mock_uow: Any) -> None:
        company_id = CompanyId(uuid4())
        role_id = RoleId(uuid4())
        user_id = UserId(uuid4())

        # Simular un rol con permisos de admin
        perm = Permission(module=PermissionModule.ADMIN, can_delete=True)
        role = Role(
            id=role_id,
            empresa_id=company_id,
            nombre="SuperAdmin",
            descripcion="Admin rol",
            permisos=[perm]
        )
        mock_uow.roles.get_by_id.return_value = role

        # Simular usuario
        mock_user = MagicMock()
        mock_user.empresa_id = company_id
        mock_uow.users.get_by_id.return_value = mock_user

        # Simular que el usuario ya tiene el rol
        mock_uow.roles.get_user_roles.return_value = [role]

        # Simular que quedan 0 admins si excluimos a este usuario
        mock_uow.roles.count_admin_users.return_value = 0

        use_case = RevokeRoleFromUserUseCase(uow=mock_uow)
        with pytest.raises(LastAdminRevocationError):
            await use_case.execute(str(company_id.value), str(role_id.value), str(user_id.value))

        mock_uow.roles.count_admin_users.assert_called_once_with(
            empresa_id=company_id, exclude_user_id=user_id
        )
        mock_uow.roles.revoke_from_user.assert_not_called()

    async def test_revoke_role_is_idempotent_when_user_does_not_have_role(self, mock_uow: Any) -> None:
        company_id = CompanyId(uuid4())
        role_id = RoleId(uuid4())
        user_id = UserId(uuid4())

        # Simular un rol
        role = Role(
            id=role_id,
            empresa_id=company_id,
            nombre="SuperAdmin",
            descripcion="Admin rol",
            permisos=[]
        )
        mock_uow.roles.get_by_id.return_value = role

        # Simular usuario
        mock_user = MagicMock()
        mock_user.empresa_id = company_id
        mock_uow.users.get_by_id.return_value = mock_user

        # Simular que el usuario NO tiene el rol (get_user_roles retorna lista vacia)
        mock_uow.roles.get_user_roles.return_value = []

        use_case = RevokeRoleFromUserUseCase(uow=mock_uow)

        # Cambiamos role.record_revocation a un mock para verificar si se llama
        role.record_revocation = MagicMock()  # type: ignore[method-assign]

        await use_case.execute(str(company_id.value), str(role_id.value), str(user_id.value))

        role.record_revocation.assert_not_called()
        mock_uow.roles.revoke_from_user.assert_not_called()


class TestAssignRoleToUserUseCase:

    async def test_assign_role_is_idempotent_when_user_already_has_role(self, mock_uow: Any) -> None:
        from app.application.use_cases.role.assign_role import AssignRoleToUserUseCase

        company_id = CompanyId(uuid4())
        role_id = RoleId(uuid4())
        user_id = UserId(uuid4())

        # Simular un rol
        role = Role(
            id=role_id,
            empresa_id=company_id,
            nombre="SuperAdmin",
            descripcion="Admin rol",
            permisos=[]
        )
        mock_uow.roles.get_by_id.return_value = role

        # Simular usuario
        mock_user = MagicMock()
        mock_user.empresa_id = company_id
        mock_uow.users.get_by_id.return_value = mock_user

        # Simular que el usuario ya tiene el rol
        mock_uow.roles.get_user_roles.return_value = [role]
        mock_uow.roles.assign_to_user.return_value = False

        use_case = AssignRoleToUserUseCase(uow=mock_uow)

        # Cambiamos role.record_assignment a un mock para verificar si se llama
        role.record_assignment = MagicMock()  # type: ignore[method-assign]

        await use_case.execute(str(company_id.value), str(role_id.value), str(user_id.value))

        role.record_assignment.assert_not_called()
        mock_uow.roles.assign_to_user.assert_called_once_with(role_id, user_id)

    async def test_create_role_with_duplicate_modules_deduplicates(self, mock_uow: Any) -> None:
        from app.application.dtos.role_dtos import CreateRoleRequest, PermissionDTO
        from app.application.use_cases.role.create_role import CreateRoleUseCase

        company_id = CompanyId(uuid4())
        mock_uow.roles.list_by_company = AsyncMock(return_value=[])
        mock_uow.roles.save = AsyncMock()

        use_case = CreateRoleUseCase(uow=mock_uow)
        request = CreateRoleRequest(
            nombre="CustomRole",
            descripcion="Desc",
            permisos=[
                PermissionDTO(module="activos", can_view=True, can_create=False, can_edit=False, can_delete=False),
                PermissionDTO(module="activos", can_view=False, can_create=True, can_edit=True, can_delete=True),
            ]
        )

        resp = await use_case.execute(str(company_id.value), request)
        assert len(resp.permisos) == 1
        assert resp.permisos[0].can_create is True

