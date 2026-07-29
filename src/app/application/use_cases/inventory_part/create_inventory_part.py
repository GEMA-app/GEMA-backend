"""Caso de Uso para registrar un repuesto en el inventario."""

from app.application.dtos.inventory_part_dtos import (
    CreateInventoryPartRequest,
    InventoryPartResponse,
)
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.entities.inventory_part import InventoryPart
from app.domain.events import InventoryPartCreated
from app.domain.value_objects import ArticleId, CompanyId, ProviderId


class CreateInventoryPartUseCase:
    """Registra un nuevo repuesto en el inventario de la empresa."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(
        self, company_id_str: str, request: CreateInventoryPartRequest
    ) -> InventoryPartResponse:
        """Crea un repuesto validando las reglas de dominio y abriendo transacción."""
        company_id = CompanyId.from_string(company_id_str)
        articulo_id = ArticleId.from_string(request.articulo_id)
        proveedor_id = ProviderId.from_string(request.proveedor_id)

        async with self.uow:
            # Delegamos la lógica e instanciación a la fábrica de la entidad de dominio
            inventory_part = InventoryPart.create(
                empresa_id=company_id,
                articulo_id=articulo_id,
                proveedor_id=proveedor_id,
                stock_minimo=request.stock_minimo,
                ubicacion_almacen=request.ubicacion_almacen,
                precio_unitario=request.precio_unitario,
                stock_inicial=request.stock_inicial,
                moneda=request.moneda,
            )

            await self.uow.inventory_parts.save(inventory_part)

            self.uow.add_event(
                InventoryPartCreated(
                    part_id=str(inventory_part.id),
                    empresa_id=company_id_str,
                )
            )
            await self.uow.commit()

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
