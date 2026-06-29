"""Fábricas de dependencias para los casos de uso de intervenciones."""

from fastapi import Depends

from app.application.ports.unit_of_work import UnitOfWorkPort
from app.application.use_cases.intervention import (
    CreateInterventionUseCase,
    DeleteInterventionUseCase,
    GetInterventionUseCase,
    ListInterventionsUseCase,
    UpdateInterventionUseCase,
)
from app.composition.container.common import get_uow


async def get_create_intervention_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> CreateInterventionUseCase:
    """Fábrica de dependencias para el caso de uso de creación de intervención.

    Args:
        uow: Unidad de trabajo inyectada.

    Returns:
        Instancia del caso de uso CreateInterventionUseCase.
    """
    return CreateInterventionUseCase(uow)


async def get_intervention_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> GetInterventionUseCase:
    """Fábrica de dependencias para el caso de uso de consulta de intervención.

    Args:
        uow: Unidad de trabajo inyectada.

    Returns:
        Instancia del caso de uso GetInterventionUseCase.
    """
    return GetInterventionUseCase(uow)


async def get_list_interventions_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> ListInterventionsUseCase:
    """Fábrica de dependencias para el caso de uso de listado de intervenciones.

    Args:
        uow: Unidad de trabajo inyectada.

    Returns:
        Instancia del caso de uso ListInterventionsUseCase.
    """
    return ListInterventionsUseCase(uow)


async def get_update_intervention_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> UpdateInterventionUseCase:
    """Fábrica de dependencias para el caso de uso de actualización de intervención.

    Args:
        uow: Unidad de trabajo inyectada.

    Returns:
        Instancia del caso de uso UpdateInterventionUseCase.
    """
    return UpdateInterventionUseCase(uow)


async def get_delete_intervention_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> DeleteInterventionUseCase:
    """Fábrica de dependencias para el caso de uso de eliminación de intervención.

    Args:
        uow: Unidad de trabajo inyectada.

    Returns:
        Instancia del caso de uso DeleteInterventionUseCase.
    """
    return DeleteInterventionUseCase(uow)
