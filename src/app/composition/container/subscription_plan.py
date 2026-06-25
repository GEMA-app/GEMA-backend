""""Fábricas de dependencias para los casos de uso de planes de subscripcion."""

from fastapi import Depends

from app.application.ports.unit_of_work import UnitOfWorkPort
from app.application.use_cases.subscription_plan import (
    CreateSubscriptionPlanUseCase,
    UpdateSubscriptionPlanUseCase,
    GetSubscriptionPlanUseCase,
    DeleteSubscriptionPlanUseCase,
    ListSubscriptionPlansUseCase
)
from app.composition.container.common import get_uow

async def get_create_subscription_plan_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> CreateSubscriptionPlanUseCase:
    """Fábrica de dependencias para el caso de uso de creación de planes de subscripcion."""
    return CreateSubscriptionPlanUseCase(uow)


async def get_subscription_plan_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> GetSubscriptionPlanUseCase:
    """Fábrica de dependencias para el caso de uso de consulta de planes de subscripcion."""
    return GetSubscriptionPlanUseCase(uow)


async def get_list_subscription_plans_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> ListSubscriptionPlansUseCase:
    """Fábrica de dependencias para el caso de uso de listado de planes de subscripcion."""
    return ListSubscriptionPlansUseCase(uow)


async def get_update_subscription_plan_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> UpdateSubscriptionPlanUseCase:
    """Fábrica de dependencias para el caso de uso de actualización de planes de subscripcion."""
    return UpdateSubscriptionPlanUseCase(uow)


async def get_delete_subscription_plan_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> DeleteSubscriptionPlanUseCase:
    """Fábrica de dependencias para el caso de uso de eliminación de planes de subscripcion."""
    return DeleteSubscriptionPlanUseCase(uow)
