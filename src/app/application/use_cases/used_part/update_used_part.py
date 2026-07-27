"""Caso de uso: actualizar un UsedPart."""

from datetime import datetime
from uuid import UUID

from app.application.dtos.used_part_dtos import (
    UpdateUsedPartRequest,
    UsedPartResponse,
)
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.exceptions.used_part import UsedPartNotFoundError
from app.domain.value_objects import CompanyId


class UpdateUsedPartUseCase:
    """Caso de uso para actualizar un repuesto utilizado."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(
        self, company_id_str: str, used_part_id: UUID, request: UpdateUsedPartRequest
    ) -> UsedPartResponse:
        """Ejecuta la actualización de un repuesto utilizado.

        Args:
            company_id_str: UUID de la empresa (tenant).
            used_part_id: UUID del repuesto a actualizar.
            request: DTO con los campos a actualizar.

        Returns:
            UsedPartResponse actualizado.

        Raises:
            UsedPartNotFoundError: Si no existe el repuesto.
        """
        company_id = CompanyId.from_string(company_id_str)

        async with self.uow:
            part = await self.uow.used_parts.get_by_id(used_part_id, company_id)
            if part is None:
                raise UsedPartNotFoundError(str(used_part_id))

            if request.cantidad_usada is not None and request.cantidad_usada != part.cantidad_usada:
                delta = request.cantidad_usada - part.cantidad_usada
                if delta > 0:
                    await self.uow.inventory_parts.validate_and_decrement_stock(
                        repuesto_id=part.repuesto_id,
                        cantidad=delta,
                        empresa_id=company_id,
                    )
                else:
                    await self.uow.inventory_parts.restore_stock(
                        repuesto_id=part.repuesto_id,
                        cantidad=abs(delta),
                        empresa_id=company_id,
                    )
                part = part.change_quantity(request.cantidad_usada)
                await self.uow.used_parts.save(part)
                await self.uow.commit()

        return UsedPartResponse(
            id=part.id,
            empresa_id=part.empresa_id.value,
            intervencion_id=part.intervencion_id,
            repuesto_id=part.repuesto_id,
            cantidad_usada=part.cantidad_usada,
            precio_unitario=part.precio_unitario,
            moneda=part.moneda,
            created_at=part.created_at or datetime.now(),
            updated_at=part.updated_at or datetime.now(),
            precio_total=(
                part.cantidad_usada * part.precio_unitario
                if part.precio_unitario is not None
                else None
            ),
        )
