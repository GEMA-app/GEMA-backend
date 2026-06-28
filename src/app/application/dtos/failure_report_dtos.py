"""DTOs de entrada y salida para el módulo de reportes de falla."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class CreateFailureReportRequest:
    """DTO de entrada para crear un reporte de falla."""

    empresa_id: str
    title: str
    description: str
    location: str
    priority: str
    reported_by: str


@dataclass(frozen=True)
class UpdateFailureReportRequest:
    """DTO de entrada para la actualización parcial de un reporte de falla."""

    title: str | None = None
    description: str | None = None
    location: str | None = None
    priority: str | None = None
    reported_by: str | None = None
    status: str | None = None
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
class FailureReportResponse:
    """DTO de salida con los datos completos de un reporte de falla."""

    id: str
    empresa_id: str
    title: str
    description: str
    location: str
    priority: str
    reported_by: str
    status: str
    created_at: str
    version: int = 1
