"""Caso de Uso para actualizar un repuesto en el inventario."""

from app.application.dtos.inventory_part_dtos import (
    InventoryPartResponse,
    UpdateInventoryPartRequest,
)
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.exceptions import InventoryPartNotFoundError, StaleDataError
from app.domain.value_objects import CompanyId, ProviderId, RepuestoId


class UpdateInventoryPartUseCase:
    """Actualiza de forma parcial y controlada los datos de un repuesto."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(
        self, company_id_str: str, part_id_str: str, request: UpdateInventoryPartRequest
    ) -> InventoryPartResponse:
        """Actualiza detalles permitidos controlando la versión del registro."""
        company_id = CompanyId.from_string(company_id_str)
        part_id = RepuestoId.from_string(part_id_str)

        async with self.uow:
            # 1. Obtener la entidad actual
            inventory_part = await self.uow.inventory_parts.get_by_id(part_id, company_id)
            if not inventory_part:
                raise InventoryPartNotFoundError(
                    f"El repuesto con ID '{part_id_str}' no existe en esta empresa."
                )

            # 2. Control de concurrencia optimista (Optimistic Locking Mixin)
            if request.version is not None and request.version != inventory_part.version:
                raise StaleDataError(
                    f"Conflicto de versión para Repuesto: se esperaba {request.version}, "
                    f"la actual es {inventory_part.version}."
                )

            # 3. Mapear campos mutables basados en _fields_set (Igual que Location)
            # Extraemos los valores actuales por si el request no los incluyó
            current_proveedor_id = inventory_part.proveedor_id
            current_stock_minimo = inventory_part.stock_minimo
            current_ubicacion = inventory_part.ubicacion_almacen
            current_precio = inventory_part.precio_unitario
            current_moneda = inventory_part.moneda

            if 'proveedor_id' in request._fields_set and request.proveedor_id is not None:
                current_proveedor_id = ProviderId.from_string(request.proveedor_id)

            if 'stock_minimo' in request._fields_set and request.stock_minimo is not None:
                current_stock_minimo = request.stock_minimo

            if 'ubicacion_almacen' in request._fields_set and request.ubicacion_almacen is not None:
                current_ubicacion = request.ubicacion_almacen

            if 'precio_unitario' in request._fields_set and request.precio_unitario is not None:
                current_precio = request.precio_unitario

            if 'moneda' in request._fields_set and request.moneda is not None:
                current_moneda = request.moneda

            # 4. Pasar los datos limpios al método con comportamiento de la Entidad
            inventory_part.update_details(
                proveedor_id=current_proveedor_id,
                stock_minimo=current_stock_minimo,
                ubicacion_almacen=current_ubicacion,
                precio_unitario=current_precio,
                moneda=current_moneda
            )

            # 5. Persistir y confirmar
            await self.uow.inventory_parts.save(inventory_part)
            await self.uow.commit()

            # 6. Recargar para obtener version incrementada y timestamps frescos de la BD
            recargado = await self.uow.inventory_parts.get_by_id(
                inventory_part.id, inventory_part.empresa_id
            )
            if recargado:
                inventory_part = recargado

            return InventoryPartResponse(
                id=str(inventory_part.id),
                empresa_id=str(inventory_part.empresa_id),
                articulo_id=str(inventory_part.articulo_id),
                proveedor_id=str(inventory_part.proveedor_id),
                stock_actual=inventory_part.stock_actual,
                stock_minimo=inventory_part.stock_minimo,
                ubicacion_almacen=inventory_part.ubicacion_almacen,
                precio_unitario=inventory_part.precio_unitario,
                moneda=inventory_part.moneda,
                version=inventory_part.version,
            )
