"""Caso de uso para obtener una categoría de artículo por ID."""

import uuid

from app.application.dtos.article_category_dtos import ArticleCategoryResponse
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.exceptions import ArticleCategoryNotFoundError


class GetArticleCategoryByIdUseCase:
    """Obtiene una categoría de artículo por su ID dentro del tenant."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(
        self, empresa_id_str: str, category_id: uuid.UUID
    ) -> ArticleCategoryResponse:
        """Ejecuta la obtención de una categoría por ID.

        Args:
            empresa_id_str: UUID de la empresa como string.
            category_id: UUID de la categoría a buscar.

        Returns:
            DTO con los datos de la categoría encontrada.

        Raises:
            ArticleCategoryNotFoundError: Si no se encuentra la categoría.
        """
        empresa_id = uuid.UUID(empresa_id_str)
        async with self.uow:
            category = await self.uow.article_categories.get_by_id(
                category_id, empresa_id
            )
            if not category:
                raise ArticleCategoryNotFoundError(
                    "Categoría de catálogo no encontrada."
                )
            await self.uow.commit()
            return ArticleCategoryResponse(
                id=category.id,
                empresa_id=category.empresa_id,
                name=category.name,
                description=category.description,
                version=category.version,
            )
