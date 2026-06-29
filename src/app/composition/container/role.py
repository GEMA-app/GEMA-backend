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
    """Fábrica de dependencias para el caso de uso de creación de rol.

    Args:
        uow: Unidad de trabajo inyectada.

    Returns:
        Instancia del caso de uso CreateRoleUseCase.
    """
    return CreateRoleUseCase(uow)


async def get_role_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> GetRoleUseCase:
    """Fábrica de dependencias para el caso de uso de consulta de rol.

    Args:
        uow: Unidad de trabajo inyectada.

    Returns:
        Instancia del caso de uso GetRoleUseCase.
    """
    return GetRoleUseCase(uow)


async def get_list_roles_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> ListRolesUseCase:
    """Fábrica de dependencias para el caso de uso de listado de roles.

    Args:
        uow: Unidad de trabajo inyectada.

    Returns:
        Instancia del caso de uso ListRolesUseCase.
    """
    return ListRolesUseCase(uow)


async def get_update_role_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> UpdateRoleUseCase:
    """Fábrica de dependencias para el caso de uso de actualización de rol.

    Args:
        uow: Unidad de trabajo inyectada.

    Returns:
        Instancia del caso de uso UpdateRoleUseCase.
    """
    return UpdateRoleUseCase(uow)


async def get_delete_role_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> DeleteRoleUseCase:
    """Fábrica de dependencias para el caso de uso de eliminación de rol.

    Args:
        uow: Unidad de trabajo inyectada.

    Returns:
        Instancia del caso de uso DeleteRoleUseCase.
    """
    return DeleteRoleUseCase(uow)


async def get_assign_role_to_user_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> AssignRoleToUserUseCase:
    """Fábrica de dependencias para el caso de uso de asignación de rol.

    Args:
        uow: Unidad de trabajo inyectada.

    Returns:
        Instancia del caso de uso AssignRoleToUserUseCase.
    """
    return AssignRoleToUserUseCase(uow=uow)


async def get_revoke_role_from_user_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> RevokeRoleFromUserUseCase:
    """Fábrica de dependencias para el caso de uso de revocación de rol.

    Args:
        uow: Unidad de trabajo inyectada.

    Returns:
        Instancia del caso de uso RevokeRoleFromUserUseCase.
    """
    return RevokeRoleFromUserUseCase(uow)
