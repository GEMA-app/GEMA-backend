from uuid import UUID

from app.application.dtos.repuesto_utilizado_dtos import RepuestoUtilizadoResponse
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.exceptions import RepuestoUtilizadoNotFoundError


class GetRepuestoUtilizadoUseCase:
    """Caso de uso para obtener un repuesto utilizado por su ID."""

    def __init__(self, uow: UnitOfWorkPort):
        self.uow = uow

    async def execute(self, repuesto_utilizado_id: UUID) -> RepuestoUtilizadoResponse:
        async with self.uow:
            repuesto = await self.uow.repuestos_utilizados.get_by_id(repuesto_utilizado_id)

        if repuesto is None:
            raise RepuestoUtilizadoNotFoundError(str(repuesto_utilizado_id))

        return RepuestoUtilizadoResponse(
            id=repuesto.id,
            empresa_id=repuesto.empresa_id.value,
            intervencion_id=repuesto.intervencion_id.value,
            repuesto_id=repuesto.repuesto_id.value,
            cantidad_usada=repuesto.cantidad_usada,
            precio_unitario=repuesto.precio_unitario,
            moneda=repuesto.moneda,
            created_at=repuesto.created_at,
            updated_at=repuesto.updated_at,
        )