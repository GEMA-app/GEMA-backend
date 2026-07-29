"""Caso de uso: eliminar un UsedPart."""

from uuid import UUID

from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.events import UsedPartDeleted
from app.domain.exceptions.used_part import UsedPartNotFoundError
from app.domain.value_objects import CompanyId


class DeleteUsedPartUseCase:
    """Caso de uso para eliminar un repuesto utilizado."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(self, company_id_str: str, used_part_id: UUID) -> None:
        """Ejecuta la eliminación de un repuesto utilizado.

        Args:
            company_id_str: UUID de la empresa (tenant).
            used_part_id: UUID del repuesto a eliminar.

        Raises:
            UsedPartNotFoundError: Si no existe el repuesto.
        """
        company_id = CompanyId.from_string(company_id_str)

        async with self.uow:
            part = await self.uow.used_parts.get_by_id(used_part_id, company_id)
            if part is None:
                raise UsedPartNotFoundError(str(used_part_id))

            await self.uow.inventory_parts.restore_stock(
                repuesto_id=part.repuesto_id,
                cantidad=part.cantidad_usada,
                empresa_id=company_id,
            )

            await self.uow.used_parts.delete(used_part_id, company_id)

            self.uow.add_event(
                UsedPartDeleted(
                    used_part_id=str(used_part_id),
                    empresa_id=company_id_str,
                )
            )

            await self.uow.commit()
