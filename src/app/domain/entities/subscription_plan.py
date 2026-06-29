"""Entidad de dominio para Planes de Suscripción."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal

from app.domain.events import DomainEvent, EventProducer
from app.domain.exceptions import SubscriptionPlanInvalidDataError
from app.domain.value_objects.identifier import SubscriptionPlanId


@dataclass
class SubscriptionPlan(EventProducer):
  """Entidad que representa un plan de suscripción."""

  id: SubscriptionPlanId
  nombre: str
  precio_mensual_usd: Decimal
  descripcion: str | None = None
  max_activos: int | None = None
  max_usuarios: int | None = None
  is_active: bool = True
  created_at: datetime | None = None
  updated_at: datetime | None = None
  _events: list[DomainEvent] = field(default_factory=list, init=False, repr=False)

  @classmethod
  def create(
    cls,
    nombre: str,
    descripcion: str | None,
    max_activos: int | None,
    max_usuarios: int | None,
    precio_mensual_usd: Decimal,
  ) -> "SubscriptionPlan":
    """Crea un nuevo plan de suscripción validando sus invariantes."""
    plan_id = SubscriptionPlanId(value=uuid.uuid4())
    return cls(
        id=plan_id,
        nombre=nombre,
        descripcion=descripcion,
        max_activos=max_activos,
        max_usuarios=max_usuarios,
        precio_mensual_usd=precio_mensual_usd,
    )

  def __post_init__(self) -> None:
    """Normaliza datos y valida invariantes del plan."""
    self._validate()

  def _validate(self) -> None:
    """Aplica las reglas de negocio del plan."""
    if not self.nombre or not self.nombre.strip():
        raise SubscriptionPlanInvalidDataError("El nombre del plan no puede estar vacío.")
    if self.precio_mensual_usd < 0:
        raise SubscriptionPlanInvalidDataError("El precio mensual no puede ser negativo.")
    if self.max_activos is not None and self.max_activos < 0:
        raise SubscriptionPlanInvalidDataError(
            "El número máximo de activos no puede ser negativo."
        )
    if self.max_usuarios is not None and self.max_usuarios < 0:
        raise SubscriptionPlanInvalidDataError(
            "El número máximo de usuarios no puede ser negativo."
        )

  @property
  def is_unlimited(self) -> bool:
    """Indica si el plan no impone límites de capacidad."""
    return self.max_activos is None or self.max_usuarios is None

  def activate(self) -> None:
    """Activa el plan si estaba inactivo."""
    self.is_active = True

  def deactivate(self) -> None:
    """Desactiva el plan si estaba activo."""
    self.is_active = False

  def update_details(self, nombre: str, descripcion: str | None) -> None:
    """Actualiza el nombre y la descripción del plan."""
    if not nombre or not nombre.strip():
        raise SubscriptionPlanInvalidDataError("El nombre del plan no puede estar vacío.")
    self.nombre = nombre.strip()
    self.descripcion = descripcion.strip() if descripcion else None

  def update_pricing(self, precio_mensual_usd: Decimal) -> None:
    """Actualiza el precio mensual del plan."""
    if precio_mensual_usd < 0:
        raise SubscriptionPlanInvalidDataError("El precio mensual no puede ser negativo.")
    self.precio_mensual_usd = precio_mensual_usd

  def update_limits(self, max_activos: int | None, max_usuarios: int | None) -> None:
    """Actualiza los límites de usuarios y activos del plan."""
    if max_activos is not None and max_activos < 0:
        raise SubscriptionPlanInvalidDataError(
            "El número máximo de activos no puede ser negativo."
        )
    if max_usuarios is not None and max_usuarios < 0:
        raise SubscriptionPlanInvalidDataError(
            "El número máximo de usuarios no puede ser negativo."
        )
    self.max_activos = max_activos
    self.max_usuarios = max_usuarios

  def can_support(self, num_users: int, num_assets: int) -> bool:
    """Determina si el plan soporta la cantidad de usuarios y activos solicitados."""
    if num_users < 0 or num_assets < 0:
        raise SubscriptionPlanInvalidDataError("Los valores de capacidad no pueden ser negativos.")

    if not self.is_active:
        return False

    if self.max_usuarios is not None and num_users > self.max_usuarios:
        return False

    if self.max_activos is not None and num_assets > self.max_activos:  # noqa: SIM103
        return False

    return True

  def can_add_user(self, current_users: int) -> bool:
    """Indica si el plan permite agregar un usuario adicional dado el uso actual."""
    if current_users < 0:
      raise SubscriptionPlanInvalidDataError("El uso actual no puede ser negativo.")

    # Preguntamos si el plan soporta el total que tendríamos al sumar 1
    return self.can_support(num_users=current_users + 1, num_assets=0)

  def can_add_asset(self, current_assets: int) -> bool:
    """Indica si el plan permite agregar un activo adicional dado el uso actual."""
    if current_assets < 0:
      raise SubscriptionPlanInvalidDataError("El uso actual no puede ser negativo.")

    # Preguntamos si el plan soporta el total que tendríamos al sumar 1
    return self.can_support(num_users=0, num_assets=current_assets + 1)

  def pull_events(self) -> list[DomainEvent]:
    """Extrae y limpia la lista de eventos acumulados."""
    events = self._events.copy()
    self._events.clear()
    return events
