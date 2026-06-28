"""Caso de uso para crear una categoría de artículo en el catálogo."""

import uuid

from app.application.dtos.article_category_dtos import (
    ArticleCategoryResponse,
    CreateCategoryRequest,
)
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.entities.article_category import ArticleCategory
from app.domain.exceptions import ArticleCategoryNameExistsError


class CreateArticleCategoryUseCase:
    """Crea una nueva categoría de artículo en la empresa validando unicidad de nombre."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(
        self, empresa_id_str: str, request: CreateCategoryRequest
    ) -> ArticleCategoryResponse:
        """Ejecuta la creación de una categoría de artículo.

        Args:
            empresa_id_str: UUID de la empresa como string.
            request: DTO con nombre y descripción de la categoría.

        Returns:
            DTO con los datos de la categoría creada.

        Raises:
            ArticleCategoryNameExistsError: Si ya existe una categoría con el
                mismo nombre en la empresa.
        """
        empresa_id = uuid.UUID(empresa_id_str)
        async with self.uow:
            existing = await self.uow.article_categories.get_by_name(
                request.name, empresa_id
            )
            if existing:
                raise ArticleCategoryNameExistsError(
                    f"La categoría '{request.name}' ya existe."
                )
            category = ArticleCategory.create(
                id=uuid.uuid4(),
                empresa_id=empresa_id,
                name=request.name,
                description=request.description,
            )
            await self.uow.article_categories.save(category)
            await self.uow.commit()
            return ArticleCategoryResponse(
                id=category.id,
                empresa_id=category.empresa_id,
                name=category.name,
                description=category.description,
                version=category.version,
            )
