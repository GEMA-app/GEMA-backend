"""Entidad InventoryPart — Gestión del inventario de repuestos con control de stock."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal

from app.domain.events import DomainEvent, EventProducer
from app.domain.exceptions import (
    EmptyStockLocationError,
    InvalidPriceError,
    InvalidStockError,
)
from app.domain.value_objects import ArticleId, CompanyId, ProviderId, RepuestoId


@dataclass
class InventoryPart(EventProducer):
    """Entidad de dominio con comportamiento que representa un repuesto en el inventario."""

    id: RepuestoId
    empresa_id: CompanyId
    articulo_id: ArticleId
    proveedor_id: ProviderId
    stock_actual: int
    stock_minimo: int
    ubicacion_almacen: str
    precio_unitario: Decimal
    moneda: str = "USD"
    version: int = 1
    created_at: datetime | None = None
    updated_at: datetime | None = None
    _events: list[DomainEvent] = field(default_factory=list, init=False, repr=False)

    def pull_events(self) -> list[DomainEvent]:
        """Extrae y limpia la lista de eventos acumulados."""
        events = self._events.copy()
        self._events.clear()
        return events

    @classmethod
    def create(
        cls,
        empresa_id: CompanyId,
        articulo_id: ArticleId,
        proveedor_id: ProviderId,
        stock_minimo: int,
        ubicacion_almacen: str,
        precio_unitario: Decimal,
        stock_inicial: int = 0,
        moneda: str = "USD",
    ) -> "InventoryPart":
        """Crea un nuevo repuesto en el inventario validando reglas iniciales.

        Raises:
            InvalidStockError: Si los valores de stock son negativos.
            InvalidPriceError: Si el precio es menor que cero.
            EmptyStockLocationError: Si la ubicación está vacía.
        """
        if stock_inicial < 0 or stock_minimo < 0:
            raise InvalidStockError("El stock inicial y el stock mínimo no pueden ser negativos.")

        if precio_unitario < Decimal("0.00"):
            raise InvalidPriceError("El precio unitario no puede ser negativo.")

        if not ubicacion_almacen or not ubicacion_almacen.strip():
            raise EmptyStockLocationError("La ubicación en almacén es obligatoria.")

        return cls(
            id=RepuestoId(uuid.uuid4()),
            empresa_id=empresa_id,
            articulo_id=articulo_id,
            proveedor_id=proveedor_id,
            stock_actual=stock_inicial,
            stock_minimo=stock_minimo,
            ubicacion_almacen=ubicacion_almacen.strip(),
            precio_unitario=precio_unitario,
            moneda=moneda,
        )

    def update_details(
        self,
        proveedor_id: ProviderId,
        stock_minimo: int,
        ubicacion_almacen: str,
        precio_unitario: Decimal,
        moneda: str,
    ) -> None:
        """Actualiza los datos permitidos del repuesto.

        NOTA DE ARQUITECTURA: 'stock_actual' NO se modifica aquí según reglas de negocio de GEMA.
        """
        if stock_minimo < 0:
            raise InvalidStockError("El stock mínimo no puede ser negativo.")

        if precio_unitario < Decimal("0.00"):
            raise InvalidPriceError("El precio unitario no puede ser negativo.")

        if not ubicacion_almacen or not ubicacion_almacen.strip():
            raise EmptyStockLocationError("La ubicación en almacén no puede estar vacía.")

        self.proveedor_id = proveedor_id
        self.stock_minimo = stock_minimo
        self.ubicacion_almacen = ubicacion_almacen.strip()
        self.precio_unitario = precio_unitario
        self.moneda = moneda

    def registrar_entrada(self, cantidad: int) -> None:
        """Incrementa el stock actual validando que la cantidad sea positiva."""
        if cantidad <= 0:
            raise InvalidStockError("La cantidad a ingresar debe ser mayor que cero.")

        self.stock_actual += cantidad

    def registrar_salida(self, cantidad: int) -> None:
        """Decrementa el stock actual validando existencias suficientes."""
        if cantidad <= 0:
            raise InvalidStockError("La cantidad a retirar debe ser mayor que cero.")

        if self.stock_actual < cantidad:
            raise InvalidStockError(
                f"Stock insuficiente. Disponible: {self.stock_actual}, Requerido: {cantidad}."
            )

        self.stock_actual -= cantidad
