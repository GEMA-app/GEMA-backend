"""Fábricas de dependencias para los casos de uso de usuarios."""

from fastapi import Depends

from app.application.ports.unit_of_work import UnitOfWorkPort
from app.application.use_cases.user import (
    CreateUserUseCase,
    UpdateUserUseCase,
    # ... casos de uso de usuarios pendientes (Get, Delete, etc.) ...
)
from app.composition.container.common import get_uow


async def get_create_user_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> CreateUserUseCase:
    """Fábrica de dependencias para el caso de uso de creación de usuarios."""
    return CreateUserUseCase(uow)


async def get_update_user_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> UpdateUserUseCase:
    """Fábrica de dependencias para el caso de uso de actualización de usuarios."""
    return UpdateUserUseCase(uow)