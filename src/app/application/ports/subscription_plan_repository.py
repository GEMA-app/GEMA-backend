from typing import Protocol

from app.domain.entities.subscription_plan import SubscriptionPlan
from app.domain.value_objects.identifier import SubscriptionPlanId


class SubscriptionPlanRepositoryPort(Protocol):
    """Interfaz para el repositorio de planes de suscripción."""

    async def save(self, plan: SubscriptionPlan) -> None:
        """Guarda un plan de suscripción en el repositorio."""
        ...

    async def get_by_id(self, plan_id: SubscriptionPlanId) -> SubscriptionPlan | None:
        """Obtiene un plan de suscripción por su identificador."""
        ...

    async def get_by_name(self, nombre: str) -> SubscriptionPlan | None:
        """Obtiene un plan de suscripción por su nombre."""
        ...

    async def list_all_plans(self, offset: int, limit: int) -> tuple[list[SubscriptionPlan], int]:
        """Lista todos los planes de suscripción con paginación."""
        ...

    async def list_active_plans(self) -> list[SubscriptionPlan]:
        """Lista todos los planes de suscripción activos."""
        ...

    async def delete(self, plan_id: SubscriptionPlanId) -> None:
        """Elimina un plan de suscripción por su identificador."""
        ...
