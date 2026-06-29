"""DTOs (Data Transfer Objects) para InventoryPart — Totalmente homologados con el estándar GEMA."""

from dataclasses import dataclass, field
from decimal import Decimal


@dataclass(frozen=True)
class CreateInventoryPartRequest:
    """DTO de entrada para la creación de un nuevo repuesto en inventario."""

    articulo_id: str
    proveedor_id: str
    stock_minimo: int
    ubicacion_almacen: str
    precio_unitario: Decimal
    stock_inicial: int = 0
    moneda: str = "USD"


@dataclass(frozen=True)
class UpdateInventoryPartRequest:
    """DTO de entrada para la actualización parcial de un repuesto.
    
    NOTA: 'stock_actual' está omitido intencionalmente ya que no se permite
    su edición directa según las reglas de negocio del inventario de GEMA.
    """

    proveedor_id: str | None = None
    stock_minimo: int | None = None
    ubicacion_almacen: str | None = None
    precio_unitario: Decimal | None = None
    moneda: str | None = None
    version: int | None = None
    _fields_set: frozenset[str] = field(default_factory=frozenset, repr=False, compare=False)

    def __post_init__(self) -> None:
        """Calcula el conjunto de campos explícitamente establecidos en la inicialización."""
        if not self._fields_set:
            fields_with_values = {
                name for name, val in self.__dict__.items()
                if name != "_fields_set" and val is not None
            }
            object.__setattr__(self, "_fields_set", frozenset(fields_with_values))


@dataclass(frozen=True)
class InventoryPartResponse:
    """DTO de salida con los datos completos de un repuesto en el inventario."""

    id: str
    empresa_id: str
    articulo_id: str
    proveedor_id: str
    stock_actual: int
    stock_minimo: int
    ubicacion_almacen: str
    precio_unitario: Decimal
    moneda: str
    version: int
    
@dataclass(frozen=True)
class InventoryPartQueryFilter:
    """DTO opcional para capturar los filtros de búsqueda en el listado global."""

    articulo_id: str | None = None