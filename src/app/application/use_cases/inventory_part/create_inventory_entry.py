"""Caso de Uso para registrar un movimiento (Entrada/Salida) de inventario."""

import uuid

from app.application.dtos.inventory_part_dtos import (
    CreateInventoryEntryRequest,
    InventoryEntryResponse,
)
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.exceptions import InventoryPartNotFoundError
from app.domain.value_objects import CompanyId, RepuestoId


class CreateInventoryEntryUseCase:
    """Registra una entrada o salida de repuestos delegando el comportamiento al dominio."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(
        self, company_id_str: str, request: CreateInventoryEntryRequest
    ) -> InventoryEntryResponse:
        """Registra el movimiento, altera el stock del repuesto y guarda en la BD."""
        company_id = CompanyId.from_string(company_id_str)
        part_id = RepuestoId.from_string(request.repuesto_id)

        async with self.uow:
            # 1. Buscar el repuesto en el repositorio (entidad de dominio)
            inventory_part = await self.uow.inventory_parts.get_by_id(part_id, company_id)
            if not inventory_part:
                raise InventoryPartNotFoundError(
                    f"El repuesto con ID '{request.repuesto_id}' no existe en esta empresa."
                )

            # 2. Delegamos la lógica de negocio a los métodos seguros de tu entidad
            if request.movement_type == "entrada":
                inventory_part.registrar_entrada(request.quantity)
            elif request.movement_type == "salida":
                inventory_part.registrar_salida(request.quantity)
            else:
                raise ValueError(f"Tipo de movimiento inválido: {request.movement_type}")

            # 3. Generar el ID del movimiento e inyectarlo en la entidad si tu modelo
            # almacena la lista de movimientos internamente antes de persistir,
            # o dejar que el mapper de infraestructura asocie los cambios.
            movimiento_id = uuid.uuid4()

            # 4. Guardar los cambios del repuesto mediante el Unit of Work existente.
            # Al pasar 'inventory_part', el repositorio de infraestructura se encarga de
            # detectar los cambios del stock_actual (y opcionalmente añadir el registro).
            await self.uow.inventory_parts.save(inventory_part)
            await self.uow.commit()

            return InventoryEntryResponse(
                id=str(movimiento_id),
                empresa_id=str(company_id),
                repuesto_id=str(part_id.value),
                movement_type=request.movement_type,
                quantity=request.quantity,
                work_order_id=request.work_order_id,
                reason=request.reason,
            )
