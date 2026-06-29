"""Caso de uso para listar todas las categorías de artículo de una empresa."""

import uuid

from app.application.dtos.article_category_dtos import ArticleCategoryResponse
from app.application.ports.unit_of_work import UnitOfWorkPort


class GetAllArticleCategoriesUseCase:
    """Lista todas las categorías de artículo de un tenant."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(
        self, empresa_id_str: str
    ) -> list[ArticleCategoryResponse]:
        """Ejecuta la obtención de todas las categorías de la empresa.

        Args:
            empresa_id_str: UUID de la empresa como string.

        Returns:
            Lista de DTOs con los datos de las categorías encontradas.
        """
        empresa_id = uuid.UUID(empresa_id_str)
        async with self.uow:
            categories = await self.uow.article_categories.get_all_by_company(
                empresa_id
            )
            await self.uow.commit()
            return [
                ArticleCategoryResponse(
                    id=c.id,
                    empresa_id=c.empresa_id,
                    name=c.name,
                    description=c.description,
                    version=c.version,
                    articulos_count=c.articulos_count,
                )
                for c in categories
            ]
