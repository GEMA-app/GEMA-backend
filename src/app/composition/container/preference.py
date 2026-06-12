"""Fábricas de dependencias para los casos de uso de preferencias."""

from fastapi import Depends

from app.application.ports.unit_of_work import UnitOfWorkPort
from app.application.use_cases.preferences import (
    GetUserPreferencesUseCase,
    UpdateUserPreferencesUseCase,
)
from app.composition.container.common import get_uow


async def get_user_preferences_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> GetUserPreferencesUseCase:
    """Fábrica de dependencias para el caso de uso de consulta de preferencias del usuario."""
    return GetUserPreferencesUseCase(uow)


async def get_update_preferences_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> UpdateUserPreferencesUseCase:
    """Fábrica de dependencias para el caso de uso de actualización de preferencias del usuario."""
    return UpdateUserPreferencesUseCase(uow)
