"""Caso de uso para actualizar una categoría de artículo existente."""

import uuid

from app.application.dtos.article_category_dtos import (
    ArticleCategoryResponse,
    UpdateCategoryRequest,
)
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.exceptions import (
    ArticleCategoryNameExistsError,
    ArticleCategoryNotFoundError,
)


class UpdateArticleCategoryUseCase:
    """Actualiza el nombre y/o descripción de una categoría validando unicidad."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(
        self,
        empresa_id_str: str,
        category_id: uuid.UUID,
        request: UpdateCategoryRequest,
    ) -> ArticleCategoryResponse:
        """Ejecuta la actualización de una categoría de artículo.

        Args:
            empresa_id_str: UUID de la empresa como string.
            category_id: UUID de la categoría a actualizar.
            request: DTO con los campos a actualizar (name y/o description).

        Returns:
            DTO con los datos de la categoría actualizada.

        Raises:
            ArticleCategoryNotFoundError: Si no se encuentra la categoría.
        """
        from app.domain.value_objects import CompanyId

        company_id = CompanyId.from_string(empresa_id_str)
        async with self.uow:
            category = await self.uow.article_categories.get_by_id(category_id, company_id.value)
            if not category:
                raise ArticleCategoryNotFoundError("Categoría no encontrada.")

            if (
                "name" in request._fields_set
                and request.name is not None
                and request.name != category.name
            ):
                existing = await self.uow.article_categories.get_by_name(
                    request.name, company_id.value
                )
                if existing:
                    raise ArticleCategoryNameExistsError(
                        f"El nombre '{request.name}' ya está en uso."
                    )
                category.change_name(request.name)

            if "description" in request._fields_set:
                category.change_description(request.description)

            await self.uow.article_categories.save(category)
            await self.uow.commit()
            return ArticleCategoryResponse(
                id=category.id,
                empresa_id=category.empresa_id,
                name=category.name,
                description=category.description,
                version=category.version,
            )
