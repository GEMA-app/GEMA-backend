from fastapi import Depends
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.application.use_cases.system_audit.get_system_audit import GetSystemAuditUseCase
from app.application.use_cases.system_audit.list_system_audits import ListSystemAuditsUseCase
from app.infrastructure.db.session import get_uow 


def get_list_system_audits_use_case(uow: UnitOfWorkPort = Depends(get_uow)) -> ListSystemAuditsUseCase:
    """Proveedor de dependencias para el caso de uso de listado."""
    return ListSystemAuditsUseCase(uow)


def get_system_audit_use_case(uow: UnitOfWorkPort = Depends(get_uow)) -> GetSystemAuditUseCase:
    """Proveedor de dependencias para el caso de uso de detalle."""
    return GetSystemAuditUseCase(uow)