"""Fábricas de inyección de dependencias para el módulo de auditoría de sistema."""

from fastapi import Depends

from app.application.ports.unit_of_work import UnitOfWorkPort
from app.application.use_cases.system_audit import GetSystemAuditUseCase, ListSystemAuditsUseCase
from app.composition.container.common import get_uow


async def get_system_audit_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> GetSystemAuditUseCase:
    """Fábrica para el caso de uso de obtener detalle de auditoría.

    Args:
        uow: Unidad de trabajo inyectada.

    Returns:
        Instancia de GetSystemAuditUseCase.
    """
    return GetSystemAuditUseCase(uow=uow)


async def get_list_system_audits_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> ListSystemAuditsUseCase:
    """Fábrica para el caso de uso de listar auditorías.

    Args:
        uow: Unidad de trabajo inyectada.

    Returns:
        Instancia de ListSystemAuditsUseCase.
    """
    return ListSystemAuditsUseCase(uow=uow)
