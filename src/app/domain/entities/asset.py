"""Entidad Asset — activo físico de la empresa con seguimiento de estado y ubicación."""

import uuid
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import ClassVar

from app.domain.enums import AssetStatus
from app.domain.events import (
    AssetCreated,
    AssetDecommissioned,
    AssetLocationChanged,
    AssetMaintenanceStarted,
    AssetOutOfService,
    AssetPutInService,
    AssetUpdated,
    DomainEvent,
    EventProducer,
)
from app.domain.exceptions import (
    AssetInvalidTransitionError,
    EmptyAssetCodeError,
    EmptySerialError,
)
from app.domain.value_objects import AssetId, CompanyId, LocationId


@dataclass
class Asset(EventProducer):
    """Entidad con comportamiento (Rich Entity) que representa un activo físico de la empresa."""

    id: AssetId
    empresa_id: CompanyId
    articulo_id: uuid.UUID
    ubicacion_id: LocationId | None
    serial_interno: str
    codigo_activo: str
    estado: AssetStatus
    fecha_adquisicion: date | None = None
    valor_monetario: Decimal | None = None
    moneda: str = "USD"
    version: int = 1
    created_at: datetime | None = None
    updated_at: datetime | None = None
    _events: list[DomainEvent] = field(default_factory=list, init=False, repr=False)

    # Máquina de estados explícita: cada estado enumera sus transiciones válidas.
    # Agregar un estado nuevo = actualizar este dict + crear método _transition_to.
    _VALID_TRANSITIONS: ClassVar[dict[AssetStatus, set[AssetStatus]]] = {
        AssetStatus.OPERATIONAL: {
            AssetStatus.UNDER_MAINTENANCE,
            AssetStatus.OUT_OF_SERVICE,
            AssetStatus.DECOMMISSIONED,
        },
        AssetStatus.UNDER_MAINTENANCE: {
            AssetStatus.OPERATIONAL,
            AssetStatus.OUT_OF_SERVICE,
            AssetStatus.DECOMMISSIONED,
        },
        AssetStatus.OUT_OF_SERVICE: {
            AssetStatus.OPERATIONAL,
            AssetStatus.UNDER_MAINTENANCE,
            AssetStatus.DECOMMISSIONED,
        },
        AssetStatus.DECOMMISSIONED: set(),
    }

    def pull_events(self) -> list[DomainEvent]:
        """Extrae y limpia la lista de eventos acumulados.

        Returns:
            La lista de eventos de dominio acumulados, vaciando la lista interna.
        """
        events = self._events.copy()
        self._events.clear()
        return events

    @classmethod
    def create(
        cls,
        empresa_id: CompanyId,
        articulo_id: uuid.UUID,
        ubicacion_id: LocationId | None,
        serial_interno: str,
        codigo_activo: str,
        estado: AssetStatus = AssetStatus.OPERATIONAL,
        fecha_adquisicion: date | None = None,
        valor_monetario: Decimal | None = None,
        moneda: str = "USD",
    ) -> "Asset":
        """Crea un nuevo activo y emite AssetCreated.

        Args:
            empresa_id: Identificador de la empresa propietaria.
            articulo_id: Identificador del artículo de catálogo.
            ubicacion_id: Identificador de la ubicación del activo.
            serial_interno: Número de serie interno del activo.
            codigo_activo: Código único del activo en la empresa.
            estado: Estado inicial del activo.
            fecha_adquisicion: Fecha de adquisición del activo.
            valor_monetario: Valor monetario del activo.
            moneda: Moneda del valor monetario.

        Returns:
            El nuevo activo creado con el evento AssetCreated emitido.

        Raises:
            EmptySerialError: Si el número de serie está vacío.
            EmptyAssetCodeError: Si el código del activo está vacío.
        """
        if not serial_interno or not serial_interno.strip():
            raise EmptySerialError("El número de serie no puede estar vacío.")
        if not codigo_activo or not codigo_activo.strip():
            raise EmptyAssetCodeError("El código del activo no puede estar vacío.")

        asset = cls(
            id=AssetId(uuid.uuid4()),
            empresa_id=empresa_id,
            articulo_id=articulo_id,
            ubicacion_id=ubicacion_id,
            serial_interno=serial_interno.strip(),
            codigo_activo=codigo_activo.strip(),
            estado=estado,
            fecha_adquisicion=fecha_adquisicion,
            valor_monetario=valor_monetario,
            moneda=moneda,
        )
        asset._events.append(
            AssetCreated(
                asset_id=str(asset.id),
                empresa_id=str(empresa_id),
                codigo_activo=asset.codigo_activo,
            )
        )
        return asset

    def _transition_to(self, new_status: AssetStatus, event: DomainEvent) -> None:
        """Valida y ejecuta una transición de estado, emitiendo el evento.

        Args:
            new_status: El estado destino al que se desea transicionar.
            event: El evento de dominio a emitir si la transición es válida.

        Raises:
            AssetInvalidTransitionError: Si la transición no está permitida
                desde el estado actual.
        """
        if new_status == self.estado:
            return
        allowed = self._VALID_TRANSITIONS.get(self.estado, set())
        if new_status not in allowed:
            raise AssetInvalidTransitionError(
                f"No se puede transicionar de '{self.estado.value}' a '{new_status.value}'."
            )
        self.estado = new_status
        self._events.append(event)

    def mark_as_under_maintenance(self) -> None:
        """Cambia el estado del activo a 'en mantenimiento'."""
        self._transition_to(
            AssetStatus.UNDER_MAINTENANCE,
            AssetMaintenanceStarted(asset_id=str(self.id)),
        )

    def decommission(self) -> None:
        """Da de baja el activo definitivamente.

        Es idempotente: si el activo ya está dado de baja, es no-op.
        """
        self._transition_to(
            AssetStatus.DECOMMISSIONED,
            AssetDecommissioned(asset_id=str(self.id)),
        )

    def put_in_service(self) -> None:
        """Reactiva un activo (de OUT_OF_SERVICE o UNDER_MAINTENANCE a OPERATIONAL)."""
        self._transition_to(
            AssetStatus.OPERATIONAL,
            AssetPutInService(asset_id=str(self.id)),
        )

    def take_out_of_service(self) -> None:
        """Marca el activo como fuera de servicio."""
        self._transition_to(
            AssetStatus.OUT_OF_SERVICE,
            AssetOutOfService(asset_id=str(self.id)),
        )

    def transfer_location(self, new_location_id: LocationId | None) -> None:
        """Cambia la ubicación del activo y emite el evento.

        Args:
            new_location_id: Identificador de la nueva ubicación, o None para desvincular.
        """
        old_location = self.ubicacion_id
        self.ubicacion_id = new_location_id
        self._events.append(
            AssetLocationChanged(
                asset_id=str(self.id),
                previous_location_id=str(old_location) if old_location else None,
                new_location_id=str(new_location_id) if new_location_id else None,
            )
        )

    def update_attributes(
        self,
        serial_interno: str | None = None,
        codigo_activo: str | None = None,
        valor_monetario: Decimal | None = None,
        moneda: str | None = None,
        fecha_adquisicion: date | None = None,
    ) -> None:
        """Actualiza los atributos base del activo y emite AssetUpdated.

        Args:
            serial_interno: Nuevo número de serie (opcional).
            codigo_activo: Nuevo código del activo (opcional).
            valor_monetario: Nuevo valor monetario (opcional).
            moneda: Nueva moneda (opcional).
            fecha_adquisicion: Nueva fecha de adquisición (opcional).

        Raises:
            EmptySerialError: Si el nuevo serial está vacío.
            EmptyAssetCodeError: Si el nuevo código está vacío.
        """
        if serial_interno is not None:
            if not serial_interno.strip():
                raise EmptySerialError("El número de serie no puede estar vacío.")
            self.serial_interno = serial_interno.strip()
        if codigo_activo is not None:
            if not codigo_activo.strip():
                raise EmptyAssetCodeError("El código del activo no puede estar vacío.")
            self.codigo_activo = codigo_activo.strip()
        if valor_monetario is not None:
            self.valor_monetario = valor_monetario
        if moneda is not None:
            self.moneda = moneda
        if fecha_adquisicion is not None:
            self.fecha_adquisicion = fecha_adquisicion
        self._events.append(
            AssetUpdated(
                asset_id=str(self.id),
                empresa_id=str(self.empresa_id),
                codigo_activo=self.codigo_activo,
            )
        )
