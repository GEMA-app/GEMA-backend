"""Fábricas de dependencias para los casos de uso de roles."""

from fastapi import Depends

from app.application.ports.unit_of_work import UnitOfWorkPort
from app.application.use_cases.role import (
    AssignRoleToUserUseCase,
    CreateRoleUseCase,
    DeleteRoleUseCase,
    GetRoleUseCase,
    ListRolesUseCase,
    RevokeRoleFromUserUseCase,
    UpdateRoleUseCase,
)
from app.composition.container.common import get_uow


async def get_create_role_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> CreateRoleUseCase:
    return CreateRoleUseCase(uow)


async def provide_role_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> GetRoleUseCase:
    return GetRoleUseCase(uow)


async def get_list_roles_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> ListRolesUseCase:
    return ListRolesUseCase(uow)


async def get_update_role_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> UpdateRoleUseCase:
    return UpdateRoleUseCase(uow)


async def get_delete_role_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> DeleteRoleUseCase:
    return DeleteRoleUseCase(uow)


async def get_assign_role_to_user_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> AssignRoleToUserUseCase:
    return AssignRoleToUserUseCase(uow)


async def get_revoke_role_from_user_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> RevokeRoleFromUserUseCase:
    return RevokeRoleFromUserUseCase(uow)
