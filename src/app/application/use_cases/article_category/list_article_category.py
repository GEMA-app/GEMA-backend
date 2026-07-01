"""Caso de uso para list article category."""

from app.application.dtos.article_category_dtos import ArticleCategoryResponse
from app.application.ports.unit_of_work import UnitOfWorkPort


class ListArticleCategoriesUseCase:
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
        from app.domain.value_objects import CompanyId

        company_id = CompanyId.from_string(empresa_id_str)
        async with self.uow:
            categories = await self.uow.article_categories.get_all_by_company(
                company_id.value
            )
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
