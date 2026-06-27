"""Caso de uso para actualizar un artículo de catálogo."""

import uuid

from app.application.dtos.catalog_article_dtos import (
    CatalogArticleResponse,
    UpdateCatalogArticleRequest,
)
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.exceptions import CatalogArticleNotFoundError
from app.domain.value_objects import CompanyId


class UpdateCatalogArticleUseCase:
    """Caso de uso para actualizar un artículo de catálogo existente.

    Actualiza solo los campos provistos en el request (parcial).
    Valida que el artículo exista y pertenezca a la empresa antes de modificar.
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
        request: UpdateCatalogArticleRequest,
    ) -> CatalogArticleResponse:
        """Ejecuta la actualización parcial de un artículo de catálogo.

        Args:
            company_id_str: Identificador de la empresa como string.
            article_id_str: Identificador del artículo como string.
            request: DTO con los campos a actualizar (solo los provistos).

        Returns:
            DTO de respuesta con los datos actualizados del artículo.

        Raises:
            CatalogArticleNotFoundError: Si el artículo no existe en la empresa.
            EmptyCatalogArticleNameError: Si se intenta dejar el nombre vacío.
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

            if "name" in request._fields_set and request.name is not None:
                article.change_name(request.name)

            if "description" in request._fields_set:
                article.change_description(request.description)

            if "manufacturer" in request._fields_set:
                article.change_manufacturer(request.manufacturer)

            if "model" in request._fields_set:
                article.change_model(request.model)

            if "unit_of_measure" in request._fields_set:
                article.change_unit_of_measure(request.unit_of_measure)

            if "category_id" in request._fields_set:
                article.assign_category(
                    uuid.UUID(request.category_id) if request.category_id else None
                )

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
