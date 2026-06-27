"""Fábricas de dependencias para los casos de uso de ejecuciones de plan."""

from fastapi import Depends

from app.application.ports.unit_of_work import UnitOfWorkPort
from app.application.use_cases.plan_execution.create_plan_execution import (
    CreatePlanExecutionUseCase,
)
from app.application.use_cases.plan_execution.get_plan_execution import (
    GetPlanExecutionUseCase,
)
from app.application.use_cases.plan_execution.list_plan_execution import (
    ListPlanExecutionUseCase,
)
from app.composition.container.common import get_uow


async def create_plan_execution_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> CreatePlanExecutionUseCase:
    """Fábrica de dependencias para el caso de uso de creación de ejecución."""
    return CreatePlanExecutionUseCase(uow)


async def get_plan_execution_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> GetPlanExecutionUseCase:
    """Fábrica de dependencias para el caso de uso de consulta de ejecución."""
    return GetPlanExecutionUseCase(uow)


async def list_plan_execution_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> ListPlanExecutionUseCase:
    """Fábrica de dependencias para el caso de uso de listado de ejecuciones."""
    return ListPlanExecutionUseCase(uow)
