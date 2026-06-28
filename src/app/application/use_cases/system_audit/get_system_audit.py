from app.application.dtos.system_audit_dtos import SystemAuditResponse
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.exceptions.system_audit import SystemAuditNotFoundError
from app.domain.value_objects import CompanyId


class GetSystemAuditUseCase:
    """Caso de uso para recuperar el detalle de una auditoría específica."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(self, company_id_str: str, audit_id: int) -> SystemAuditResponse:
        """Recupera el detalle de una auditoría por ID.

        Args:
            company_id_str: UUID de la empresa en formato string.
            audit_id: ID numérico del registro de auditoría.

        Returns:
            SystemAuditResponse con los datos de la auditoría.

        Raises:
            SystemAuditNotFoundError: Si no existe la auditoría en la empresa.
        """
        company_id = CompanyId.from_string(company_id_str)

        async with self.uow:
            audit = await self.uow.system_audits.get_by_id(company_id, audit_id)
            if not audit:
                raise SystemAuditNotFoundError(audit_id, company_id_str)

            return SystemAuditResponse(
                id=audit.id if audit.id is not None else 0,
                empresa_id=str(audit.empresa_id),
                usuario_id=str(audit.usuario_id) if audit.usuario_id else None,
                accion=audit.accion,
                detalles=audit.detalles,
                ip_address=audit.ip_address,
                ocurrido_en=audit.ocurrido_en,
            )
