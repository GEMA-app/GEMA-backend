from uuid import UUID
from sqlalchemy import select, delete
from app.application.ports.article_category_repository import ArticleCategoryRepositoryPort
from app.domain.entities.article_category import ArticleCategory
from app.infrastructure.db.models.article_category import ArticleCategoryModel
from app.infrastructure.repositories.sqlalchemy_repository import SqlAlchemyRepository

class SqlAlchemyArticleCategoryRepository(SqlAlchemyRepository[ArticleCategoryModel], ArticleCategoryRepositoryPort):
    def _to_entity(self, model: ArticleCategoryModel) -> ArticleCategory:
        # SÍ mapea timestamps y version desde el modelo ORM a la Entidad de Dominio
        return ArticleCategory(
            id=model.id,
            empresa_id=model.empresa_id,
            nombre=model.nombre,
            descripcion=model.descripcion,
            version=model.version,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    def _to_model(self, entity: ArticleCategory) -> ArticleCategoryModel:
        # NO mapea timestamps (deja que los maneje TimestampMixin de la BD)
        # SÍ incluye version para concurrencia optimista (VersionMixin)
        return ArticleCategoryModel(
            id=entity.id,
            empresa_id=entity.empresa_id,
            nombre=entity.nombre,
            descripcion=entity.descripcion,
            version=entity.version
        )

    async def get_by_id(self, category_id: UUID, empresa_id: UUID) -> ArticleCategory | None:
        stmt = select(ArticleCategoryModel).where(
            ArticleCategoryModel.id == category_id,
            ArticleCategoryModel.empresa_id == empresa_id
        )
        res = await self.session.execute(stmt)
        model = res.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_name(self, nombre: str, empresa_id: UUID) -> ArticleCategory | None:
        stmt = select(ArticleCategoryModel).where(
            ArticleCategoryModel.nombre == nombre,
            ArticleCategoryModel.empresa_id == empresa_id
        )
        res = await self.session.execute(stmt)
        model = res.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_all_by_empresa(self, empresa_id: UUID) -> list[ArticleCategory]:
        stmt = select(ArticleCategoryModel).where(ArticleCategoryModel.empresa_id == empresa_id)
        res = await self.session.execute(stmt)
        models = res.scalars().all()
        return [self._to_entity(m) for m in models]

    async def delete(self, category_id: UUID, empresa_id: UUID) -> None:
        stmt = delete(ArticleCategoryModel).where(
            ArticleCategoryModel.id == category_id,
            ArticleCategoryModel.empresa_id == empresa_id
        )
        await self.session.execute(stmt)