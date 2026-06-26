"""Fábricas de dependencias para el módulo UsedPart."""

from fastapi import Depends

from app.application.ports.unit_of_work import UnitOfWorkPort
from app.application.use_cases.used_part import (
    CreateUsedPartUseCase,
    DeleteUsedPartUseCase,
    GetUsedPartUseCase,
    ListUsedPartsUseCase,
    UpdateUsedPartUseCase,
)
from app.composition.container.common import get_uow


async def get_list_used_parts_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> ListUsedPartsUseCase:
    """Fábrica para el caso de uso ListUsedPartsUseCase.

    Args:
        uow: Unidad de trabajo inyectada.

    Returns:
        Instancia de ListUsedPartsUseCase.
    """
    return ListUsedPartsUseCase(uow)


async def get_create_used_part_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> CreateUsedPartUseCase:
    """Fábrica para el caso de uso CreateUsedPartUseCase.

    Args:
        uow: Unidad de trabajo inyectada.

    Returns:
        Instancia de CreateUsedPartUseCase.
    """
    return CreateUsedPartUseCase(uow)


async def get_get_used_part_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> GetUsedPartUseCase:
    """Fábrica para el caso de uso GetUsedPartUseCase.

    Args:
        uow: Unidad de trabajo inyectada.

    Returns:
        Instancia de GetUsedPartUseCase.
    """
    return GetUsedPartUseCase(uow)


async def get_update_used_part_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> UpdateUsedPartUseCase:
    """Fábrica para el caso de uso UpdateUsedPartUseCase.

    Args:
        uow: Unidad de trabajo inyectada.

    Returns:
        Instancia de UpdateUsedPartUseCase.
    """
    return UpdateUsedPartUseCase(uow)


async def get_delete_used_part_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> DeleteUsedPartUseCase:
    """Fábrica para el caso de uso DeleteUsedPartUseCase.

    Args:
        uow: Unidad de trabajo inyectada.

    Returns:
        Instancia de DeleteUsedPartUseCase.
    """
    return DeleteUsedPartUseCase(uow)
