"""Puerto (interfaz) del repositorio para la persistencia de artículos de catálogo."""

from typing import Any, Protocol
from uuid import UUID

from app.domain.entities import CatalogArticle
from app.domain.value_objects import CompanyId


class CatalogArticleRepositoryPort(Protocol):
    """Puerto de repositorio para la persistencia y consulta de artículos de catálogo."""

    async def save(self, article: CatalogArticle) -> None:
        """Guarda o actualiza un artículo de catálogo.

        Args:
            article: Entidad del artículo a persistir.
        """
        ...

    async def get_by_id(
        self,
        article_id: UUID,
        empresa_id: CompanyId,
    ) -> CatalogArticle | None:
        """Obtiene un artículo de catálogo por su ID, validando la empresa.

        Args:
            article_id: Identificador UUID del artículo.
            empresa_id: Identificador de la empresa propietaria.

        Returns:
            El artículo si existe y pertenece a la empresa, o None.
        """
        ...

    async def list_by_company(
        self,
        empresa_id: CompanyId,
        offset: int,
        limit: int,
        filters: dict[str, Any] | None = None,
    ) -> tuple[list[CatalogArticle], int]:
        """Lista artículos de una empresa con paginación y filtros opcionales.

        Args:
            empresa_id: Identificador de la empresa.
            offset: Número de registros a saltar.
            limit: Máximo de registros a retornar.
            filters: Diccionario opcional de filtros.
                Claves soportadas: "category_id", "search".

        Returns:
            Tupla con la lista de artículos y el total de registros sin paginación.
        """
        ...

    async def delete(
        self,
        article_id: UUID,
        empresa_id: CompanyId,
    ) -> None:
        """Elimina un artículo de catálogo por su ID.

        Args:
            article_id: Identificador UUID del artículo a eliminar.
            empresa_id: Identificador de la empresa propietaria.
        """
        ...

    async def get_by_company_and_id(
        self,
        article_id: UUID,
        empresa_id: CompanyId,
    ) -> CatalogArticle | None:
        """Obtiene un artículo por ID verificando que pertenezca a la empresa.

        Args:
            article_id: Identificador UUID del artículo.
            empresa_id: Identificador de la empresa.

        Returns:
            El artículo si existe y pertenece a la empresa, o None.
        """
        ...

    async def exists_by_company_id(
        self,
        article_id: UUID,
    ) -> bool:
        """Verifica si existe un artículo de catálogo por su ID.

        Args:
            article_id: Identificador UUID del artículo.

        Returns:
            True si el artículo existe, False en caso contrario.
        """
        ...
