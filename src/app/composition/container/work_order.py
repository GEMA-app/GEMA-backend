"""Fábricas de dependencias para el módulo Work Order.

Cada función es una dependencia de FastAPI que construye y provee
el caso de uso correspondiente con su Unit of Work inyectado.
"""

from fastapi import Depends

from app.application.ports.unit_of_work import UnitOfWorkPort
from app.application.use_cases.work_order import (
    AssignTechnicianUseCase,
    ChangeWorkOrderStatusUseCase,
    CreateWorkOrderUseCase,
    DeleteWorkOrderUseCase,
    GetWorkOrderStatusHistoryUseCase,
    GetWorkOrderUseCase,
    ListWorkOrdersUseCase,
    RemoveTechnicianUseCase,
    UpdateWorkOrderUseCase,
    ValidateWorkOrderUseCase,
)
from app.composition.container.common import get_uow


async def get_create_work_order_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> CreateWorkOrderUseCase:
    """Provee el caso de uso para crear una orden de trabajo."""
    return CreateWorkOrderUseCase(uow)


async def get_work_order_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> GetWorkOrderUseCase:
    """Provee el caso de uso para obtener una orden de trabajo."""
    return GetWorkOrderUseCase(uow)


async def get_list_work_orders_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> ListWorkOrdersUseCase:
    """Provee el caso de uso para listar órdenes de trabajo."""
    return ListWorkOrdersUseCase(uow)


async def get_update_work_order_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> UpdateWorkOrderUseCase:
    """Provee el caso de uso para actualizar una orden de trabajo."""
    return UpdateWorkOrderUseCase(uow)


async def get_delete_work_order_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> DeleteWorkOrderUseCase:
    """Provee el caso de uso para eliminar una orden de trabajo."""
    return DeleteWorkOrderUseCase(uow)


async def get_change_work_order_status_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> ChangeWorkOrderStatusUseCase:
    """Provee el caso de uso para cambiar el estado de una orden."""
    return ChangeWorkOrderStatusUseCase(uow)


async def get_assign_technician_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> AssignTechnicianUseCase:
    """Provee el caso de uso para asignar un técnico."""
    return AssignTechnicianUseCase(uow)


async def get_remove_technician_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> RemoveTechnicianUseCase:
    """Provee el caso de uso para remover un técnico."""
    return RemoveTechnicianUseCase(uow)


async def get_validate_work_order_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> ValidateWorkOrderUseCase:
    """Provee el caso de uso para validar una orden de trabajo."""
    return ValidateWorkOrderUseCase(uow)


async def get_get_work_order_status_history_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> GetWorkOrderStatusHistoryUseCase:
    """Provee el caso de uso para obtener el historial de estados."""
    return GetWorkOrderStatusHistoryUseCase(uow)
