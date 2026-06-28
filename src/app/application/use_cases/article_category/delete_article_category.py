"""Caso de uso para eliminar una categoría de artículo."""

import uuid

from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.exceptions import ArticleCategoryNotFoundError


class DeleteArticleCategoryUseCase:
    """Elimina una categoría de artículo por su ID dentro del tenant."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(
        self, empresa_id_str: str, category_id: uuid.UUID
    ) -> None:
        """Ejecuta la eliminación de una categoría de artículo.

        Args:
            empresa_id_str: UUID de la empresa como string.
            category_id: UUID de la categoría a eliminar.

        Raises:
            ArticleCategoryNotFoundError: Si no se encuentra la categoría.
        """
        empresa_id = uuid.UUID(empresa_id_str)
        async with self.uow:
            category = await self.uow.article_categories.get_by_id(
                category_id, empresa_id
            )
            if not category:
                raise ArticleCategoryNotFoundError("Categoría no encontrada.")
            await self.uow.article_categories.delete(category.id, empresa_id)
            await self.uow.commit()
