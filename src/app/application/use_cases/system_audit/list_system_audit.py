"""Caso de uso para list system audit."""

from app.application.dtos.system_audit_dtos import ListSystemAuditsRequest, SystemAuditResponse
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.value_objects import CompanyId


class ListSystemAuditsUseCase:
    """Caso de uso para listar y filtrar auditorías del sistema."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(
        self,
        company_id_str: str,
        offset: int,
        limit: int,
        request: ListSystemAuditsRequest,
    ) -> tuple[list[SystemAuditResponse], int]:
        """Lista y filtra las auditorías del sistema con paginación.

        Args:
            company_id_str: UUID de la empresa en formato string.
            offset: Número de registros a saltar.
            limit: Máximo de registros por página.
            request: DTO con filtros opcionales (usuario_id, accion, fechas).

        Returns:
            Tupla con la lista de SystemAuditResponse y el total de registros.
        """
        company_id = CompanyId.from_string(company_id_str)

        filters: dict[str, object] = {}
        if request.usuario_id is not None:
            filters["usuario_id"] = request.usuario_id
        if request.accion:
            filters["accion"] = request.accion
        if request.modulo:
            filters["modulo"] = request.modulo
        if request.fecha_inicio:
            filters["fecha_inicio"] = request.fecha_inicio
        if request.fecha_fin:
            filters["fecha_fin"] = request.fecha_fin

        async with self.uow:
            entities, total = await self.uow.system_audits.get_all_by_company(
                company_id, offset, limit, filters
            )

            dtos = [
                SystemAuditResponse(
                    id=str(e.id) if e.id is not None else "",
                    empresa_id=str(e.empresa_id),
                    usuario_id=str(e.usuario_id) if e.usuario_id else None,
                    accion=e.accion,
                    detalles=e.detalles,
                    ip_address=e.ip_address,
                    ocurrido_en=e.ocurrido_en,
                    usuario_nombre=e.usuario_nombre,
                    usuario_email=e.usuario_email,
                )
                for e in entities
            ]


            return dtos, total
