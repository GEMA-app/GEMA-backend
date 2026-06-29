"""Caso de uso para obtener un artículo de catálogo por su ID."""

import uuid

from app.application.dtos.catalog_article_dtos import CatalogArticleResponse
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.exceptions import CatalogArticleNotFoundError
from app.domain.value_objects import CompanyId


class GetCatalogArticleUseCase:
    """Caso de uso para obtener un artículo de catálogo por su ID.

    Verifica que el artículo exista y pertenezca a la empresa especificada.
    """

    def __init__(self, uow: UnitOfWorkPort) -> None:
        """Inicializa el caso de uso con una unidad de trabajo.

        Args:
            uow: Unidad de trabajo que gestiona la transacción y los repositorios.
        """
        self._uow = uow

    async def execute(
        self,
        company_id_str: str,
        article_id_str: str,
    ) -> CatalogArticleResponse:
        """Obtiene un artículo de catálogo por su ID.

        Args:
            company_id_str: Identificador de la empresa como string.
            article_id_str: Identificador del artículo como string.

        Returns:
            DTO de respuesta con los datos del artículo.

        Raises:
            CatalogArticleNotFoundError: Si el artículo no existe en la empresa.
            InvalidUUIDError: Si algún identificador no es un UUID válido.
        """
        company_id = CompanyId.from_string(company_id_str)
        article_uuid = uuid.UUID(article_id_str)

        async with self._uow:
            article = await self._uow.catalog_articles.get_by_company_and_id(
                article_uuid, company_id
            )
            if not article:
                raise CatalogArticleNotFoundError(article_id_str)



            return CatalogArticleResponse(
                id=str(article.id),
                empresa_id=str(article.empresa_id),
                category_id=str(article.category_id) if article.category_id else None,
                name=article.name,
                description=article.description,
                manufacturer=article.manufacturer,
                model=article.model,
                unit_of_measure=article.unit_of_measure,
            )
