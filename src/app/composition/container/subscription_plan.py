"""Fábricas de dependencias para los casos de uso de planes de suscripción."""

from fastapi import Depends

from app.application.ports.unit_of_work import UnitOfWorkPort
from app.application.use_cases.subscription_plan import (
    CreateSubscriptionPlanUseCase,
    DeleteSubscriptionPlanUseCase,
    GetSubscriptionPlanUseCase,
    UpdateSubscriptionPlanUseCase,
)
from app.application.use_cases.subscription_plan.list_subscription_plan import (
    ListSubscriptionPlansUseCase,
)
from app.composition.container.common import get_uow


async def get_create_subscription_plan_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> CreateSubscriptionPlanUseCase:
    """Fábrica de dependencias para el caso de uso de creación de plan de suscripción.

    Args:
        uow: Unidad de trabajo inyectada.

    Returns:
        Instancia del caso de uso CreateSubscriptionPlanUseCase.
    """
    return CreateSubscriptionPlanUseCase(uow)


async def get_subscription_plan_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> GetSubscriptionPlanUseCase:
    """Fábrica de dependencias para el caso de uso de consulta de plan de suscripción.

    Args:
        uow: Unidad de trabajo inyectada.

    Returns:
        Instancia del caso de uso GetSubscriptionPlanUseCase.
    """
    return GetSubscriptionPlanUseCase(uow)


async def get_list_subscription_plans_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> ListSubscriptionPlansUseCase:
    """Fábrica de dependencias para el caso de uso de listado de planes de suscripción.

    Args:
        uow: Unidad de trabajo inyectada.

    Returns:
        Instancia del caso de uso ListSubscriptionPlansUseCase.
    """
    return ListSubscriptionPlansUseCase(uow)


async def get_update_subscription_plan_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> UpdateSubscriptionPlanUseCase:
    """Fábrica de dependencias para el caso de uso de actualización de plan de suscripción.

    Args:
        uow: Unidad de trabajo inyectada.

    Returns:
        Instancia del caso de uso UpdateSubscriptionPlanUseCase.
    """
    return UpdateSubscriptionPlanUseCase(uow)


async def get_delete_subscription_plan_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> DeleteSubscriptionPlanUseCase:
    """Fábrica de dependencias para el caso de uso de eliminación de plan de suscripción.

    Args:
        uow: Unidad de trabajo inyectada.

    Returns:
        Instancia del caso de uso DeleteSubscriptionPlanUseCase.
    """
    return DeleteSubscriptionPlanUseCase(uow)
