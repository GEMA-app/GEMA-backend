from typing import Any, Protocol

from app.domain.entities import CatalogArticle
from app.domain.value_objects import CompanyId


class CatalogArticleRepositoryPort(Protocol):
    """Puerto de repositorio para la persistencia y consulta de artículos de catálogo."""

    async def save(self, article: CatalogArticle) -> None:
        """Guarda o actualiza un artículo."""
        ...

    async def get_by_id(
        self,
        article_id: str,
        empresa_id: CompanyId,
    ) -> CatalogArticle | None:
        """Obtiene un artículo por ID."""
        ...

    async def list_by_company(
        self,
        empresa_id: CompanyId,
        offset: int,
        limit: int,
        filters: dict[str, Any] | None = None,
    ) -> tuple[list[CatalogArticle], int]:
        """Lista artículos de una empresa."""
        ...

    async def delete(
        self,
        article_id: str,
        empresa_id: CompanyId,
    ) -> None:
        """Elimina un artículo."""
        ...