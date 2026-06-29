"""Caso de uso: listar UsedParts por intervención."""

from datetime import datetime
from uuid import UUID

from app.application.dtos.used_part_dtos import UsedPartResponse
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.value_objects import CompanyId, InterventionId


class ListUsedPartsUseCase:
    """Caso de uso para listar repuestos utilizados de una intervención."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(
        self, company_id_str: str, intervention_id: UUID
    ) -> list[UsedPartResponse]:
        """Ejecuta el listado de repuestos utilizados.

        Args:
            company_id_str: UUID de la empresa (tenant).
            intervention_id: UUID de la intervención.

        Returns:
            Lista de UsedPartResponse.
        """
        company_id = CompanyId.from_string(company_id_str)
        intervention_id_vo = InterventionId.from_string(str(intervention_id))

        async with self.uow:
            parts = await self.uow.used_parts.get_by_intervention(
                company_id, intervention_id_vo
            )

        return [
            UsedPartResponse(
                id=p.id,
                empresa_id=p.empresa_id.value,
                intervencion_id=p.intervencion_id,
                repuesto_id=p.repuesto_id,
                cantidad_usada=p.cantidad_usada,
                precio_unitario=p.precio_unitario,
                moneda=p.moneda,
                created_at=p.created_at or datetime.now(),
                updated_at=p.updated_at or datetime.now(),
                precio_total=(
                    p.cantidad_usada * p.precio_unitario
                    if p.precio_unitario is not None
                    else None
                ),
            )
            for p in parts
        ]
