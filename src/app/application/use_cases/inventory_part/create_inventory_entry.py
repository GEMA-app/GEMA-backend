"""Caso de Uso para registrar un movimiento (Entrada/Salida) de inventario."""

from uuid import UUID

from app.application.dtos.inventory_part_dtos import (
    CreateInventoryEntryRequest,
    InventoryEntryResponse,
)
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.entities.inventory_entry import InventoryEntry
from app.domain.events import InventoryEntryCreated
from app.domain.exceptions import InventoryPartNotFoundError, ValidationException
from app.domain.value_objects import CompanyId, SparePartId


class CreateInventoryEntryUseCase:
    """Registra una entrada o salida de repuestos delegando al dominio y persistiendo."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(
        self, company_id_str: str, request: CreateInventoryEntryRequest
    ) -> InventoryEntryResponse:
        """Registra el movimiento, altera el stock del repuesto y guarda en la BD."""
        company_id = CompanyId.from_string(company_id_str)
        part_id = SparePartId.from_string(request.repuesto_id)

        async with self.uow:
            # 1. Buscar el repuesto en el repositorio (entidad de dominio)
            inventory_part = await self.uow.inventory_parts.get_by_id(part_id, company_id)
            if not inventory_part:
                raise InventoryPartNotFoundError(
                    f"El repuesto con ID '{request.repuesto_id}' no existe en esta empresa."
                )

            # 2. Delegamos la lógica de negocio a los métodos seguros de tu entidad repuesto
            if request.movement_type == "entrada":
                inventory_part.record_incoming_stock(request.quantity)
            elif request.movement_type == "salida":
                inventory_part.record_outgoing_stock(request.quantity)
            else:
                msg = f"Tipo de movimiento inválido: {request.movement_type}"
                raise ValidationException(msg)

            # 3. Guardar los cambios del repuesto mediante el Unit of Work.
            await self.uow.inventory_parts.save(inventory_part)

            # 4. Crear y persistir el registro del movimiento (InventoryEntry)
            ot_id = UUID(request.work_order_id) if request.work_order_id else None
            user_id = UUID(request.usuario_id) if request.usuario_id else None

            entry = InventoryEntry.create(
                empresa_id=company_id,
                repuesto_id=part_id.value,
                cantidad=request.quantity,
                tipo_movimiento=request.movement_type,
                ordenes_trabajo_id=ot_id,
                usuario_id=user_id,
                precio_unitario=inventory_part.precio_unitario,
                moneda=inventory_part.moneda,
                observaciones=request.reason,
            )

            await self.uow.inventory_entries.save(entry)

            self.uow.add_event(
                InventoryEntryCreated(
                    entry_id=str(entry.id),
                    empresa_id=company_id_str,
                )
            )
            await self.uow.commit()

            return InventoryEntryResponse(
                id=str(entry.id),
                empresa_id=str(company_id),
                repuesto_id=str(part_id.value),
                movement_type=request.movement_type,
                quantity=request.quantity,
                work_order_id=request.work_order_id,
                usuario_id=request.usuario_id,
                precio_unitario=entry.precio_unitario,
                moneda=entry.moneda,
                fecha_movimiento=entry.fecha_movimiento.isoformat()
                if entry.fecha_movimiento
                else None,
                reason=request.reason,
            )
