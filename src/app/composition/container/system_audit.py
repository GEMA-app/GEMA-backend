from app.application.use_cases.system_audit import SystemAuditUseCase
from app.composition.container.common import get_uow

def get_system_audit_use_case() -> SystemAuditUseCase:
    """Fábrica para el caso de uso de auditoría."""
    return SystemAuditUseCase(uow=get_uow())