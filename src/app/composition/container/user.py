"""Fábricas de dependencias para los casos de uso de usuarios."""

from fastapi import Depends

from app.application.ports.auth import PasswordHasherPort
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.application.use_cases.user import (
    CreateUserUseCase,
    DeleteUserUseCase,
    EditUserUseCase,
    GetUserUseCase,
    ListUsersUseCase,
)
from app.composition.container.common import get_password_hasher, get_uow


async def get_create_user_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
    hasher: PasswordHasherPort = Depends(get_password_hasher),
) -> CreateUserUseCase:
    """Fábrica de dependencias para el caso de uso de creación de usuarios.

    Args:
        uow: Unidad de trabajo inyectada.
        hasher: Servicio de hashing inyectado.

    Returns:
        Instancia del caso de uso CreateUserUseCase.
    """
    return CreateUserUseCase(uow=uow, hasher=hasher)


async def get_user_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> GetUserUseCase:
    """Fábrica de dependencias para el caso de uso de consulta de usuarios.

    Args:
        uow: Unidad de trabajo inyectada.

    Returns:
        Instancia del caso de uso GetUserUseCase.
    """
    return GetUserUseCase(uow=uow)


async def get_edit_user_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> EditUserUseCase:
    """Fábrica de dependencias para el caso de uso de edición de usuarios.

    Args:
        uow: Unidad de trabajo inyectada.

    Returns:
        Instancia del caso de uso EditUserUseCase.
    """
    return EditUserUseCase(uow=uow)


async def get_delete_user_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> DeleteUserUseCase:
    """Fábrica de dependencias para el caso de uso de baja lógica de usuarios.

    Args:
        uow: Unidad de trabajo inyectada.

    Returns:
        Instancia del caso de uso DeleteUserUseCase.
    """
    return DeleteUserUseCase(uow=uow)


async def get_list_users_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> ListUsersUseCase:
    """Fábrica de dependencias para el caso de uso de listado de usuarios.

    Args:
        uow: Unidad de trabajo inyectada.

    Returns:
        Instancia del caso de uso ListUsersUseCase.
    """
    return ListUsersUseCase(uow=uow)
