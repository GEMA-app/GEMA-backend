"""Entidad InventoryPart — Gestión del inventario de repuestos con control de stock."""

import uuid
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from app.domain.exceptions import (
    EmptyStockLocationError,
    InvalidPriceError,
    InvalidStockError,
)
from app.domain.value_objects import ArticleId, CompanyId, ProviderId, SparePartId


@dataclass
class InventoryPart:
    """Entidad de dominio con comportamiento que representa un repuesto en el inventario."""

    id: SparePartId
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
    articulo_nombre: str | None = None
    proveedor_nombre: str | None = None

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

        Args:
            empresa_id: Identificador de la empresa propietaria.
            articulo_id: Identificador del artículo de catálogo.
            proveedor_id: Identificador del proveedor.
            stock_minimo: Cantidad mínima de stock antes de reordenar.
            ubicacion_almacen: Ubicación física en el almacén.
            precio_unitario: Precio unitario del repuesto.
            stock_inicial: Cantidad inicial en stock (por defecto 0).
            moneda: Moneda del precio (por defecto USD).

        Returns:
            Una nueva instancia de InventoryPart con los datos proporcionados.

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
            id=SparePartId(uuid.uuid4()),
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

        Args:
            proveedor_id: Nuevo identificador del proveedor.
            stock_minimo: Nuevo stock mínimo.
            ubicacion_almacen: Nueva ubicación en el almacén.
            precio_unitario: Nuevo precio unitario.
            moneda: Nueva moneda.

        Raises:
            InvalidStockError: Si el stock mínimo es negativo.
            InvalidPriceError: Si el precio unitario es negativo.
            EmptyStockLocationError: Si la ubicación en almacén está vacía.
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

    def record_incoming_stock(self, cantidad: int) -> None:
        """Incrementa el stock actual validando que la cantidad sea positiva.

        Args:
            cantidad: Cantidad a agregar al stock (debe ser mayor que cero).

        Raises:
            InvalidStockError: Si la cantidad es menor o igual a cero.
        """
        if cantidad <= 0:
            raise InvalidStockError("La cantidad a ingresar debe ser mayor que cero.")

        self.stock_actual += cantidad

    def record_outgoing_stock(self, cantidad: int) -> None:
        """Decrementa el stock actual validando existencias suficientes.

        Args:
            cantidad: Cantidad a retirar del stock (debe ser mayor que cero).

        Raises:
            InvalidStockError: Si la cantidad es menor o igual a cero,
                o si el stock disponible es insuficiente.
        """
        if cantidad <= 0:
            raise InvalidStockError("La cantidad a retirar debe ser mayor que cero.")

        if self.stock_actual < cantidad:
            raise InvalidStockError(
                f"Stock insuficiente. Disponible: {self.stock_actual}, Requerido: {cantidad}."
            )

        self.stock_actual -= cantidad
