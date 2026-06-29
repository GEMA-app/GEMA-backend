"""Factories for the technical interventions module."""

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
    """Factory for CreateInterventionUseCase.

    Initializes CreateInterventionUseCase with UnitOfWork containing
    the intervention repository.
    """
    return CreateInterventionUseCase(uow=uow)


async def get_list_interventions_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> ListInterventionsUseCase:
    """Factory for ListInterventionsUseCase.

    Initializes ListInterventionsUseCase with UnitOfWork containing
    the intervention repository.
    """
    return ListInterventionsUseCase(uow=uow)


async def get_intervention_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> GetInterventionUseCase:
    """Factory for GetInterventionUseCase.

    Initializes GetInterventionUseCase with UnitOfWork containing
    the intervention repository.
    """
    return GetInterventionUseCase(uow=uow)


async def get_update_intervention_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> UpdateInterventionUseCase:
    """Factory for UpdateInterventionUseCase.

    Initializes UpdateInterventionUseCase with UnitOfWork containing
    the intervention repository.
    """
    return UpdateInterventionUseCase(uow=uow)


async def get_delete_intervention_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> DeleteInterventionUseCase:
    """Factory for DeleteInterventionUseCase."""
    return DeleteInterventionUseCase(uow=uow)
