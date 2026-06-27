from typing import Any, Protocol, Self

from app.application.ports.article_category_repository import ArticleCategoryRepositoryPort
from app.application.ports.asset_repository import AssetRepositoryPort
from app.application.ports.company_repository import CompanyRepositoryPort
from app.application.ports.event_bus import EventBusPort
from app.application.ports.location_repository import LocationRepositoryPort
from app.application.ports.preference_repository import PreferenceRepositoryPort
from app.application.ports.repository import UserRepositoryPort
from app.application.ports.role_repository import RoleRepositoryPort


class UnitOfWorkPort(Protocol):
    """Puerto para el patrón Unit of Work, gestionando transacciones y repositorios."""

    users: UserRepositoryPort
    companies: CompanyRepositoryPort
    roles: RoleRepositoryPort
    assets: AssetRepositoryPort
    locations: LocationRepositoryPort
    event_bus: EventBusPort
    preferences: PreferenceRepositoryPort
    article_categories: ArticleCategoryRepositoryPort

    async def __aenter__(self) -> Self:
        """Inicia el contexto transaccional asíncrono."""
        ...

    async def __aexit__(self, exc_type: Any, exc_val: Any, tb: Any) -> None:
        """Cierra el contexto, ejecutando un rollback automático en caso de excepción."""
        ...

    async def commit(self) -> None:
        """Confirma los cambios pendientes en la base de datos."""
        ...

    async def rollback(self) -> None:
        """Deshace los cambios no confirmados en la transacción actual."""
        ...
