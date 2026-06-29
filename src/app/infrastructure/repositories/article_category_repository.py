"""Adaptador SQLAlchemy para el repositorio de categorías de artículos."""

from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.article_category_repository import (
    ArticleCategoryRepositoryPort,
)
from app.domain.entities.article_category import ArticleCategory
from app.domain.events import DomainEvent
from app.infrastructure.db.models import CatalogArticleModel
from app.infrastructure.db.models.article_category import ArticleCategoryModel
from app.infrastructure.repositories.base import SqlAlchemyRepository


class SqlAlchemyArticleCategoryRepository(
    SqlAlchemyRepository[ArticleCategoryModel, ArticleCategory, UUID],
    ArticleCategoryRepositoryPort,
):
    """Implementación concreta de ArticleCategoryRepositoryPort usando SQLAlchemy 2.0."""

    def __init__(
        self,
        session: AsyncSession,
        pending_events: list[DomainEvent] | None = None,
    ) -> None:
        """Inicializa el repositorio con la sesión y el modelo ORM.

        Args:
            session: Sesión asíncrona de SQLAlchemy.
            pending_events: Lista compartida para acumular eventos de dominio.
        """
        super().__init__(session, ArticleCategoryModel, pending_events)

    def _to_entity(self, model: ArticleCategoryModel) -> ArticleCategory:
        """Convierte un modelo ORM a una entidad de dominio.

        Incluye timestamps de persistencia para que los casos de uso
        puedan inspeccionarlos sin cargar el modelo ORM directamente.
        """
        return ArticleCategory(
            id=model.id,
            empresa_id=model.empresa_id,
            name=model.nombre,
            description=model.descripcion,
            version=model.version,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: ArticleCategory) -> ArticleCategoryModel:
        """Convierte una entidad de dominio a modelo ORM.

        No mapea timestamps (TimestampMixin los maneja automáticamente).
        Incluye version para optimistic locking (VersionMixin).
        """
        return ArticleCategoryModel(
            id=entity.id,
            empresa_id=entity.empresa_id,
            nombre=entity.name,
            descripcion=entity.description,
            version=entity.version,
        )

    async def get_by_id(  # type: ignore[override]
        self, category_id: UUID, empresa_id: UUID
    ) -> ArticleCategory | None:
        """Busca una categoría por ID dentro del tenant.

        Args:
            category_id: Identificador UUID de la categoría.
            empresa_id: Identificador UUID del tenant.

        Returns:
            La entidad ArticleCategory si existe, None en caso contrario.
        """
        stmt = (
            select(
                ArticleCategoryModel,
                func.count(CatalogArticleModel.id).label("articulos_count"),
            )
            .outerjoin(
                CatalogArticleModel,
                ArticleCategoryModel.id == CatalogArticleModel.category_id,
            )
            .where(
                ArticleCategoryModel.id == category_id,
                ArticleCategoryModel.empresa_id == empresa_id,
            )
            .group_by(ArticleCategoryModel.id)
        )
        res = await self.session.execute(stmt)
        row = res.first()
        if not row:
            return None
        model, count = row
        entity = self._to_entity(model)
        entity.articulos_count = count
        return entity

    async def get_by_name(
        self, name: str, empresa_id: UUID
    ) -> ArticleCategory | None:
        """Busca una categoría por nombre exacto dentro del tenant.

        Args:
            name: Nombre exacto de la categoría.
            empresa_id: Identificador UUID del tenant.

        Returns:
            La entidad ArticleCategory si existe, None en caso contrario.
        """
        stmt = select(ArticleCategoryModel).where(
            ArticleCategoryModel.nombre == name,
            ArticleCategoryModel.empresa_id == empresa_id,
        )
        res = await self.session.execute(stmt)
        model = res.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_all_by_company(self, empresa_id: UUID) -> list[ArticleCategory]:
        """Retorna todas las categorías de un tenant.

        Args:
            empresa_id: Identificador UUID del tenant.

        Returns:
            Lista de entidades ArticleCategory (vacía si no hay registros).
        """
        stmt = (
            select(
                ArticleCategoryModel,
                func.count(CatalogArticleModel.id).label("articulos_count"),
            )
            .outerjoin(
                CatalogArticleModel,
                ArticleCategoryModel.id == CatalogArticleModel.category_id,
            )
            .where(ArticleCategoryModel.empresa_id == empresa_id)
            .group_by(ArticleCategoryModel.id)
        )
        res = await self.session.execute(stmt)
        results = res.all()
        entities = []
        for model, count in results:
            entity = self._to_entity(model)
            entity.articulos_count = count
            entities.append(entity)
        return entities

    async def delete(  # type: ignore[override]
        self, category_id: UUID, empresa_id: UUID
    ) -> None:
        """Elimina una categoría por ID dentro del tenant.

        Args:
            category_id: Identificador UUID de la categoría a eliminar.
            empresa_id: Identificador UUID del tenant.
        """
        stmt = delete(ArticleCategoryModel).where(
            ArticleCategoryModel.id == category_id,
            ArticleCategoryModel.empresa_id == empresa_id,
        )
        await self.session.execute(stmt)
