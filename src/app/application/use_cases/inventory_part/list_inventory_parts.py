"""Caso de Uso para listar el inventario de repuestos con paginación."""

from app.application.dtos.inventory_part_dtos import InventoryPartResponse
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.value_objects import CompanyId


class ListInventoryPartsUseCase:
    """Recupera el listado paginado de repuestos de una empresa."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(
        self, company_id_str: str, limit: int = 20, offset: int = 0, bajo_minimo: bool = False
    ) -> tuple[list[InventoryPartResponse], int]:
        """Obtiene las entidades del repositorio y las transforma en DTOs de salida."""
        company_id = CompanyId.from_string(company_id_str)

        async with self.uow:
            # Invocamos el método de listado que definimos en el puerto del repositorio
            parts, total = await self.uow.inventory_parts.get_all_by_company(
                empresa_id=company_id, limit=limit, offset=offset, bajo_minimo=bajo_minimo
            )

            dtos = [
                InventoryPartResponse(
                    id=str(part.id),
                    empresa_id=str(part.empresa_id),
                    articulo_id=str(part.articulo_id),
                    proveedor_id=str(part.proveedor_id),
                    stock_actual=part.stock_actual,
                    stock_minimo=part.stock_minimo,
                    ubicacion_almacen=part.ubicacion_almacen,
                    precio_unitario=part.precio_unitario,
                    moneda=part.moneda,
                    version=part.version,
                )
                for part in parts
            ]
            return dtos, total
