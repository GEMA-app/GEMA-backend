from app.application.dtos.system_audit_dtos import SystemAuditResponse
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.exceptions.system_audit import SystemAuditNotFoundError
from app.domain.value_objects import CompanyId


class GetSystemAuditUseCase:
    """Caso de uso para recuperar el detalle de una auditoría específica."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(self, company_id_str: str, auditoria_id: int) -> SystemAuditResponse:
        company_id = CompanyId.from_string(company_id_str)

        async with self.uow:  # Abre sesión de lectura
            audit = await self.uow.system_audits.get_by_id(company_id, auditoria_id)
            if not audit:
                raise SystemAuditNotFoundError(auditoria_id, company_id_str)

            return SystemAuditResponse(
                id=audit.id,
                empresa_id=str(audit.empresa_id),
                usuario_id=int(audit.usuario_id) if audit.usuario_id else None,
                accion=audit.accion,
                detalles=audit.detalles,
                ip_address=audit.ip_address,
                ocurrido_en=audit.ocurrido_en,
            )