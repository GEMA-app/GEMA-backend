from uuid import UUID

from app.application.dtos.repuesto_utilizado_dtos import RepuestoUtilizadoResponse
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.value_objects import UserId


class ListRepuestosUtilizadosUseCase:
    """Caso de uso para listar repuestos utilizados de una intervención."""

    def __init__(self, uow: UnitOfWorkPort):
        self.uow = uow

    async def execute(self, company_id_str: str, intervention_id: UUID) -> list[RepuestoUtilizadoResponse]:
        company_id = UserId.from_string(company_id_str)

        async with self.uow:
            repuestos = await self.uow.repuestos_utilizados.get_by_intervention(
                company_id, intervention_id
            )

        return [
            RepuestoUtilizadoResponse(
                id=r.id,
                empresa_id=r.empresa_id.value,
                intervencion_id=r.intervencion_id,
                repuesto_id=r.repuesto_id,
                cantidad_usada=r.cantidad_usada,
                precio_unitario=r.precio_unitario,
                moneda=r.moneda,
                created_at=r.created_at,
                updated_at=r.updated_at,
            )
            for r in repuestos
        ]