import uuid

from app.application.dtos.catalog_article_dtos import (
    CatalogArticleResponse,
    CreateCatalogArticleRequest,
)
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.entities import CatalogArticle
from app.domain.value_objects import CompanyId


class CreateCatalogArticleUseCase:
    """Caso de uso para crear un artículo del catálogo."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(
        self,
        company_id_str: str,
        request: CreateCatalogArticleRequest,
    ) -> CatalogArticleResponse:
        """Crea un artículo de catálogo y lo persiste."""
        company_id = CompanyId.from_string(company_id_str)

        async with self.uow:
            article = CatalogArticle(
                id=uuid.uuid4(),
                empresa_id=company_id.value,
                categoria_id=(
                    uuid.UUID(request.categoria_id)
                    if request.categoria_id
                    else None
                ),
                nombre=request.nombre.strip(),
                descripcion=request.descripcion,
                fabricante=request.fabricante,
                modelo=request.modelo,
                unidad_medida=request.unidad_medida,
            )

            await self.uow.catalog_articles.save(article)
            await self.uow.commit()

            return CatalogArticleResponse(
                id=str(article.id),
                empresa_id=str(article.empresa_id),
                categoria_id=(
                    str(article.categoria_id)
                    if article.categoria_id
                    else None
                ),
                nombre=article.nombre,
                descripcion=article.descripcion,
                fabricante=article.fabricante,
                modelo=article.modelo,
                unidad_medida=article.unidad_medida,
            )