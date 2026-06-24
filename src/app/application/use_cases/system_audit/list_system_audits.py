from typing import List, Tuple
from app.application.dtos.system_audit_dtos import ListSystemAuditsRequest, SystemAuditResponse
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.value_objects import CompanyId


class ListSystemAuditsUseCase:
    """Caso de uso para listar y filtrar auditorías del sistema."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(
        self, company_id_str: str, offset: int, limit: int, request: ListSystemAuditsRequest
    ) -> Tuple[List[SystemAuditResponse], int]:
        company_id = CompanyId.from_string(company_id_str)

        # Mapeamos el DTO de filtros a un diccionario limpio para el puerto
        filters = {}
        if request.usuario_id is not None:
            filters["usuario_id"] = request.usuario_id
        if request.accion:
            filters["accion"] = request.accion
        if request.fecha_inicio:
            filters["fecha_inicio"] = request.fecha_inicio
        if request.fecha_fin:
            filters["fecha_fin"] = request.fecha_fin

        async with self.uow:
            entities, total = await self.uow.system_audits.get_all_by_empresa(
                company_id, offset, limit, filters
            )

            dtos = [
                SystemAuditResponse(
                    id=e.id,
                    empresa_id=str(e.empresa_id),
                    usuario_id=int(e.usuario_id) if e.usuario_id else None,
                    accion=e.accion,
                    detalles=e.detalles,
                    ip_address=e.ip_address,
                    ocurrido_en=e.ocurrido_en,
                )
                for e in entities
            ]

            return dtos, total