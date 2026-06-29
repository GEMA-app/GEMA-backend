"""Fábricas de dependencias para los casos de uso de ejecución de planes."""

from fastapi import Depends

from app.application.ports.unit_of_work import UnitOfWorkPort
from app.application.use_cases.plan_execution import (
    CreatePlanExecutionUseCase,
    GetPlanExecutionUseCase,
    ListPlanExecutionUseCase,
)
from app.composition.container.common import get_uow


async def get_create_plan_execution_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> CreatePlanExecutionUseCase:
    """Fábrica de dependencias para el caso de uso de creación de ejecución de plan.

    Args:
        uow: Unidad de trabajo inyectada.

    Returns:
        Instancia del caso de uso CreatePlanExecutionUseCase.
    """
    return CreatePlanExecutionUseCase(uow)


async def get_plan_execution_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> GetPlanExecutionUseCase:
    """Fábrica de dependencias para el caso de uso de consulta de ejecución de plan.

    Args:
        uow: Unidad de trabajo inyectada.

    Returns:
        Instancia del caso de uso GetPlanExecutionUseCase.
    """
    return GetPlanExecutionUseCase(uow)


async def get_list_plan_executions_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> ListPlanExecutionUseCase:
    """Fábrica de dependencias para el caso de uso de listado de ejecuciones de plan.

    Args:
        uow: Unidad de trabajo inyectada.

    Returns:
        Instancia del caso de uso ListPlanExecutionUseCase.
    """
    return ListPlanExecutionUseCase(uow)
