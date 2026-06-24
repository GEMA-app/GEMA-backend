from dataclasses import dataclass
from decimal import Decimal

@dataclass
class CreateSubscriptionPlanRequest:
    """DTO de entrada para la creación de un plan de suscripción."""

    nombre: str
    descripcion: str | None = None
    max_activos: int | None = None
    max_usuarios: int | None = None
    precio_mensual_usd: Decimal
    # start_date: str
    # end_date: str

@dataclass
class UpdateSubscriptionPlanRequest:
    """DTO de entrada para la actualización de un plan de suscripción."""

    nombre: str | None = None
    descripcion: str | None = None
    max_activos: int | None = None
    max_usuarios: int | None = None
    precio_mensual_usd: Decimal | None = None
    # start_date: str | None = None
    # end_date: str | None = None

    def __post_init__(self) -> None:
        """Calcula el conjunto de campos explícitamente establecidos en la inicialización."""
        if not self._fields_set:
            fields_with_values = {
                name for name, val in self.__dict__.items()
                if name != "_fields_set" and val is not None
            }
            object.__setattr__(self, "_fields_set", frozenset(fields_with_values))

@dataclass
class SubscriptionPlanResponse:
    """DTO de salida con los datos completos de un plan de suscripción."""

    id: str
    nombre: str
    descripcion: str
    max_activos: int | None
    max_usuarios: int | None
    precio_mensual_usd: Decimal
    # start_date: str
    # end_date: str
    is_active: bool
    version: int