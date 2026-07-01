"""Caso de uso para listar artículos de catálogo de una empresa con paginación y filtros."""

from app.application.dtos.catalog_article_dtos import CatalogArticleResponse
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.value_objects import CompanyId


class ListCatalogArticlesUseCase:
    """Caso de uso para listar artículos de catálogo de una empresa.

    Soporta paginación (offset/limit) y filtros opcionales por categoría
    y búsqueda por nombre.
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
        offset: int = 0,
        limit: int = 20,
        category_id: str | None = None,
        search: str | None = None,
    ) -> tuple[list[CatalogArticleResponse], int]:
        """Lista los artículos de catálogo de una empresa.

        Args:
            company_id_str: Identificador de la empresa como string.
            offset: Número de registros a saltar (por defecto 0).
            limit: Máximo de registros a retornar (por defecto 20).
            category_id: Filtrar por categoría (opcional).
            search: Búsqueda por nombre (opcional).

        Returns:
            Tupla con la lista de respuestas DTO y el total de registros sin paginación.

        Raises:
            InvalidUUIDError: Si company_id_str no es un UUID válido.
        """
        company_id = CompanyId.from_string(company_id_str)

        filters: dict[str, str] = {}
        if category_id:
            filters["category_id"] = category_id
        if search:
            filters["search"] = search

        async with self._uow:
            articles, total = await self._uow.catalog_articles.list_by_company(
                empresa_id=company_id,
                offset=offset,
                limit=limit,
                filters=filters if filters else None,
            )

            return (
                [
                    CatalogArticleResponse(
                        id=str(a.id),
                        empresa_id=str(a.empresa_id),
                        category_id=str(a.category_id) if a.category_id else None,
                        name=a.name,
                        description=a.description,
                        manufacturer=a.manufacturer,
                        model=a.model,
                        unit_of_measure=a.unit_of_measure,
                    )
                    for a in articles
                ],
                total,
            )
