"""Fábricas de dependencias para los casos de uso de planes de mantenimiento."""

from fastapi import Depends

from app.application.ports.unit_of_work import UnitOfWorkPort
from app.application.use_cases.maintenance_plan import (
    CreateMaintenancePlanUseCase,
    DeleteMaintenancePlanUseCase,
    GetMaintenancePlanUseCase,
    UpdateMaintenancePlanUseCase,
)
from app.application.use_cases.maintenance_plan.list_maintenance_plan import (
    ListMaintenancePlansUseCase,
)
from app.composition.container.common import get_uow


async def get_create_maintenance_plan_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> CreateMaintenancePlanUseCase:
    """Fábrica de dependencias para el caso de uso de creación de plan de mantenimiento.

    Args:
        uow: Unidad de trabajo inyectada.

    Returns:
        Instancia del caso de uso CreateMaintenancePlanUseCase.
    """
    return CreateMaintenancePlanUseCase(uow)


async def get_get_maintenance_plan_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> GetMaintenancePlanUseCase:
    """Fábrica de dependencias para el caso de uso de consulta de plan de mantenimiento.

    Args:
        uow: Unidad de trabajo inyectada.

    Returns:
        Instancia del caso de uso GetMaintenancePlanUseCase.
    """
    return GetMaintenancePlanUseCase(uow)


async def get_list_maintenance_plans_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> ListMaintenancePlansUseCase:
    """Fábrica de dependencias para el caso de uso de listado de planes de mantenimiento.

    Args:
        uow: Unidad de trabajo inyectada.

    Returns:
        Instancia del caso de uso ListMaintenancePlansUseCase.
    """
    return ListMaintenancePlansUseCase(uow)


async def get_update_maintenance_plan_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> UpdateMaintenancePlanUseCase:
    """Fábrica de dependencias para el caso de uso de actualización de plan de mantenimiento.

    Args:
        uow: Unidad de trabajo inyectada.

    Returns:
        Instancia del caso de uso UpdateMaintenancePlanUseCase.
    """
    return UpdateMaintenancePlanUseCase(uow)


async def get_delete_maintenance_plan_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> DeleteMaintenancePlanUseCase:
    """Fábrica de dependencias para el caso de uso de eliminación de plan de mantenimiento.

    Args:
        uow: Unidad de trabajo inyectada.

    Returns:
        Instancia del caso de uso DeleteMaintenancePlanUseCase.
    """
    return DeleteMaintenancePlanUseCase(uow)
