"""Caso de uso: crear un UsedPart (repuesto utilizado)."""

from datetime import datetime

from app.application.dtos.used_part_dtos import (
    CreateUsedPartRequest,
    UsedPartResponse,
)
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.entities.used_part import UsedPart
from app.domain.events import UsedPartCreated
from app.domain.value_objects import CompanyId


class CreateUsedPartUseCase:
    """Caso de uso para registrar un nuevo repuesto utilizado."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(
        self, company_id_str: str, request: CreateUsedPartRequest
    ) -> UsedPartResponse:
        """Ejecuta la creación de un repuesto utilizado.

        Valida que haya stock suficiente antes de decrementar. Si el repuesto
        de inventario no existe, se registra el consumo sin afectar stock
        (el módulo Inventory es dependencia futura planificada).

        Args:
            company_id_str: UUID de la empresa (tenant).
            request: DTO con los datos del repuesto a crear.

        Returns:
            UsedPartResponse con los datos del repuesto creado.

        Raises:
            InsufficientStockError: Si el stock disponible es menor a la
                cantidad solicitada.
        """
        company_id = CompanyId.from_string(company_id_str)

        new_part = UsedPart.create(
            empresa_id=company_id,
            intervencion_id=request.intervencion_id,
            repuesto_id=request.repuesto_id,
            cantidad_usada=request.cantidad_usada,
            precio_unitario=request.precio_unitario,
            moneda=request.moneda,
        )

        async with self.uow:
            await self.uow.inventory_parts.validate_and_decrement_stock(
                repuesto_id=request.repuesto_id,
                cantidad=request.cantidad_usada,
                empresa_id=company_id,
            )

            await self.uow.used_parts.save(new_part)

            self.uow.add_event(
                UsedPartCreated(
                    used_part_id=str(new_part.id),
                    empresa_id=company_id_str,
                )
            )

            await self.uow.commit()

        return UsedPartResponse(
            id=new_part.id,
            empresa_id=new_part.empresa_id.value,
            intervencion_id=new_part.intervencion_id,
            repuesto_id=new_part.repuesto_id,
            cantidad_usada=new_part.cantidad_usada,
            precio_unitario=new_part.precio_unitario,
            moneda=new_part.moneda,
            created_at=new_part.created_at or datetime.now(),
            updated_at=new_part.updated_at or datetime.now(),
            precio_total=new_part.precio_total,
        )
