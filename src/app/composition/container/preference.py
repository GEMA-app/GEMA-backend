"""Fábricas de dependencias para los casos de uso de preferencias de usuario."""

from fastapi import Depends

from app.application.ports.unit_of_work import UnitOfWorkPort
from app.application.use_cases.preference import (
    GetUserPreferencesUseCase,
    UpdateUserPreferencesUseCase,
)
from app.composition.container.common import get_uow


async def get_user_preference_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> GetUserPreferencesUseCase:
    """Fábrica de dependencias para el caso de uso de consulta de preferencias.

    Args:
        uow: Unidad de trabajo inyectada.

    Returns:
        Instancia del caso de uso GetUserPreferencesUseCase.
    """
    return GetUserPreferencesUseCase(uow)


async def get_update_preference_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> UpdateUserPreferencesUseCase:
    """Fábrica de dependencias para el caso de uso de actualización de preferencias.

    Args:
        uow: Unidad de trabajo inyectada.

    Returns:
        Instancia del caso de uso UpdateUserPreferencesUseCase.
    """
    return UpdateUserPreferencesUseCase(uow)
