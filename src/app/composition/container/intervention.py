"""Factories for the technical interventions module."""

from fastapi import Depends

from app.application.ports.unit_of_work import UnitOfWorkPort
from app.application.use_cases.intervention import (
    CreateInterventionUseCase,
    GetInterventionUseCase,
    ListInterventionsUseCase,
    UpdateInterventionUseCase,
)
from app.composition.container.common import get_uow


async def get_create_intervention_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> CreateInterventionUseCase:
    """Factory for CreateInterventionUseCase.

    Initializes CreateInterventionUseCase with UnitOfWork and InterventionRepositoryPort.
    """
    return CreateInterventionUseCase(
        uow=uow,
        intervention_repository=uow.interventions,
    )


async def get_list_interventions_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> ListInterventionsUseCase:
    """Factory for ListInterventionsUseCase.

    Initializes ListInterventionsUseCase with UnitOfWork and InterventionRepositoryPort.
    """
    return ListInterventionsUseCase(
        uow=uow,
        intervention_repository=uow.interventions,
    )


async def get_intervention_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> GetInterventionUseCase:
    """Factory for GetInterventionUseCase.

    Initializes GetInterventionUseCase with UnitOfWork and InterventionRepositoryPort.
    """
    return GetInterventionUseCase(
        uow=uow,
        intervention_repository=uow.interventions,
    )


async def get_update_intervention_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> UpdateInterventionUseCase:
    """Factory for UpdateInterventionUseCase.

    Initializes UpdateInterventionUseCase with UnitOfWork and InterventionRepositoryPort.
    """
    return UpdateInterventionUseCase(
        uow=uow,
        intervention_repository=uow.interventions,
    )
