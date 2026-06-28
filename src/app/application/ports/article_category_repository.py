"""Puerto (Protocol) del repositorio de categorías de artículos."""

from typing import Protocol
from uuid import UUID

from app.domain.entities.article_category import ArticleCategory


class ArticleCategoryRepositoryPort(Protocol):
    """Contrato estructural para el repositorio de categorías de artículos."""

    async def get_by_id(
        self, category_id: UUID, empresa_id: UUID
    ) -> ArticleCategory | None:
        """Busca una categoría por ID dentro del tenant."""
        ...

    async def get_by_name(
        self, name: str, empresa_id: UUID
    ) -> ArticleCategory | None:
        """Busca una categoría por nombre exacto dentro del tenant."""
        ...

    async def get_all_by_company(self, empresa_id: UUID) -> list[ArticleCategory]:
        """Retorna todas las categorías de un tenant."""
        ...

    async def save(self, category: ArticleCategory) -> None:
        """Persiste una categoría (crea o actualiza según exista)."""
        ...

    async def delete(self, category_id: UUID, empresa_id: UUID) -> None:
        """Elimina una categoría por ID dentro del tenant."""
        ...
