from dataclasses import dataclass, field
from decimal import Decimal


@dataclass(frozen=True)
class CreateSubscriptionPlanRequest:
    """DTO de entrada para la creación de un plan de suscripción."""

    nombre: str
    precio_mensual_usd: Decimal
    descripcion: str | None = None
    max_activos: int | None = None
    max_usuarios: int | None = None

@dataclass(frozen=True)
class UpdateSubscriptionPlanRequest:
    """DTO de entrada para la actualización de un plan de suscripción."""

    nombre: str | None = None
    descripcion: str | None = None
    max_activos: int | None = None
    max_usuarios: int | None = None
    precio_mensual_usd: Decimal | None = None
    is_active: bool | None = None
    _fields_set: frozenset[str] = field(
        default_factory=frozenset, init=False, repr=False, compare=False
    )

    def __post_init__(self) -> None:
        """Calcula el conjunto de campos explícitamente establecidos en la inicialización."""
        if not self._fields_set:
            fields_with_values = {
                name for name, val in self.__dict__.items()
                if name != "_fields_set" and val is not None
            }
            object.__setattr__(self, "_fields_set", frozenset(fields_with_values))

@dataclass(frozen=True)
class SubscriptionPlanResponse:
    """DTO de salida con los datos completos de un plan de suscripción."""

    id: str
    nombre: str
    precio_mensual_usd: Decimal
    descripcion: str | None = None
    max_activos: int | None = None
    max_usuarios: int | None = None
    is_active: bool = True
