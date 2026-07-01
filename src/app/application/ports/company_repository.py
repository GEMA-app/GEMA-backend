"""Puerto (Protocol) del repositorio de Company."""

from typing import Protocol

from app.domain.entities import Company
from app.domain.value_objects import CompanyId, Slug, SubscriptionPlanId


class CompanyRepositoryPort(Protocol):
    """Puerto de repositorio para la persistencia y consulta de entidades Company."""

    async def save(self, company: Company) -> None:
        """Guarda o actualiza una empresa en el repositorio."""
        ...

    async def get_by_id(self, id: CompanyId) -> Company | None:
        """Busca una empresa por su identificador único."""
        ...

    async def get_by_slug(self, slug: Slug) -> Company | None:
        """Busca una empresa por su slug único."""
        ...

    async def list_all(self, offset: int, limit: int) -> tuple[list[Company], int]:
        """Devuelve una lista paginada de empresas y el conteo total."""
        ...

    async def delete(self, id: CompanyId) -> None:
        """Elimina una empresa por su identificador único."""
        ...

    async def count_by_plan_id(self, plan_id: SubscriptionPlanId) -> int:
        """Cuenta el número de empresas asociadas a un plan de suscripción."""
        ...
