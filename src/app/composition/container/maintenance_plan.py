"""Fábricas de dependencias para el módulo MaintenancePlan.

Usa ``get_uow`` de ``common.py`` para evitar duplicación y garantizar
que el bus de eventos se inyecte correctamente.
"""

from fastapi import Depends

from app.application.ports.unit_of_work import UnitOfWorkPort
from app.application.use_cases.maintenance_plan import (
    CreateMaintenancePlanUseCase,
    DeleteMaintenancePlanUseCase,
    GetMaintenancePlanUseCase,
    ListMaintenancePlansUseCase,
    UpdateMaintenancePlanUseCase,
)
from app.composition.container.common import get_uow


async def get_create_maintenance_plan_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> CreateMaintenancePlanUseCase:
    """Provee el caso de uso de creación de plan."""
    return CreateMaintenancePlanUseCase(uow=uow)


async def get_get_maintenance_plan_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> GetMaintenancePlanUseCase:
    """Provee el caso de uso de obtención de plan."""
    return GetMaintenancePlanUseCase(uow=uow)


async def get_list_maintenance_plans_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> ListMaintenancePlansUseCase:
    """Provee el caso de uso de listado de planes."""
    return ListMaintenancePlansUseCase(uow=uow)


async def get_update_maintenance_plan_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> UpdateMaintenancePlanUseCase:
    """Provee el caso de uso de actualización de plan."""
    return UpdateMaintenancePlanUseCase(uow=uow)


async def get_delete_maintenance_plan_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> DeleteMaintenancePlanUseCase:
    """Provee el caso de uso de eliminación de plan."""
    return DeleteMaintenancePlanUseCase(uow=uow)
