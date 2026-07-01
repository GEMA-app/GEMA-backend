"""DTOs de entrada y salida para el módulo de Asset."""

from dataclasses import dataclass, field
from datetime import date


@dataclass(frozen=True)
class CreateAssetRequest:
    """DTO de entrada para la creación de un activo físico."""

    articulo_id: str
    serial_interno: str
    codigo_activo: str
    estado: str
    ubicacion_id: str | None = None
    fecha_adquisicion: date | None = None
    valor_monetario: float | None = None
    moneda: str = "USD"


@dataclass(frozen=True)
class UpdateAssetRequest:
    """DTO de entrada para la actualización parcial de un activo."""

    serial_interno: str | None = None
    codigo_activo: str | None = None
    estado: str | None = None
    ubicacion_id: str | None = None
    fecha_adquisicion: date | None = None
    valor_monetario: float | None = None
    moneda: str | None = None
    version: int | None = None
    _fields_set: frozenset[str] = field(default_factory=frozenset, repr=False, compare=False)

    def __post_init__(self) -> None:
        """Calcula el conjunto de campos explícitamente establecidos en la inicialización."""
        if not self._fields_set:
            fields_with_values = {
                name
                for name, val in self.__dict__.items()
                if name != "_fields_set" and val is not None
            }
            object.__setattr__(self, "_fields_set", frozenset(fields_with_values))


@dataclass(frozen=True)
class AssetResponse:
    """DTO de salida con los datos completos de un activo."""

    id: str
    empresa_id: str
    articulo_id: str
    ubicacion_id: str | None
    serial_interno: str
    codigo_activo: str
    estado: str
    fecha_adquisicion: str | None
    valor_monetario: float | None
    moneda: str
    version: int
