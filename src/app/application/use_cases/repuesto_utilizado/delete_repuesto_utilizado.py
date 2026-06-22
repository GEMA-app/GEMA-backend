from uuid import UUID

from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.exceptions import RepuestoUtilizadoNotFoundError


class DeleteRepuestoUtilizadoUseCase:
    """Caso de uso para eliminar un repuesto utilizado."""

    def __init__(self, uow: UnitOfWorkPort):
        self.uow = uow

    async def execute(self, repuesto_utilizado_id: UUID) -> None:
        async with self.uow:
            repuesto = await self.uow.repuestos_utilizados.get_by_id(repuesto_utilizado_id)
            if repuesto is None:
                raise RepuestoUtilizadoNotFoundError(str(repuesto_utilizado_id))

            await self.uow.repuestos_utilizados.delete(repuesto_utilizado_id)
            await self.uow.commit()