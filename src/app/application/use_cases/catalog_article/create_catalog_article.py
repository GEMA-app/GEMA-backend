"""Caso de uso para la creación de un artículo de catálogo dentro de una empresa."""

import uuid

from app.application.dtos.catalog_article_dtos import (
    CatalogArticleResponse,
    CreateCatalogArticleRequest,
)
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.entities import CatalogArticle
from app.domain.value_objects import CompanyId


class CreateCatalogArticleUseCase:
    """Caso de uso para crear un artículo del catálogo.

    Orquesta la creación de un nuevo artículo validando las reglas de negocio
    y persistiéndolo a través de la unidad de trabajo.
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
        request: CreateCatalogArticleRequest,
    ) -> CatalogArticleResponse:
        """Ejecuta la creación de un artículo de catálogo.

        Args:
            company_id_str: Identificador de la empresa como string.
            request: DTO con los datos del artículo a crear.

        Returns:
            DTO de respuesta con los datos del artículo creado.

        Raises:
            EmptyCatalogArticleNameError: Si el nombre del artículo está vacío.
            InvalidUUIDError: Si company_id_str no es un UUID válido.
        """
        company_id = CompanyId.from_string(company_id_str)

        article = CatalogArticle.create(
            empresa_id=company_id.value,
            name=request.name,
            category_id=uuid.UUID(request.category_id) if request.category_id else None,
            description=request.description,
            manufacturer=request.manufacturer,
            model=request.model,
            unit_of_measure=request.unit_of_measure,
        )

        async with self._uow:
            await self._uow.catalog_articles.save(article)
            await self._uow.commit()

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
