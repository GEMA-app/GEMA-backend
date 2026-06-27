"""Repositorio SQLAlchemy para artículos de catálogo."""

import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.catalog_repository import (
    CatalogArticleRepositoryPort,
)
from app.domain.entities import CatalogArticle
from app.domain.events import DomainEvent
from app.domain.value_objects import CompanyId
from app.infrastructure.db.models.catalog import CatalogArticleModel
from app.infrastructure.repositories.tenant_repository import (
    SqlAlchemyTenantRepository,
)


class SqlAlchemyCatalogArticleRepository(
    SqlAlchemyTenantRepository[
        CatalogArticleModel,
        CatalogArticle,
        uuid.UUID,
    ],
    CatalogArticleRepositoryPort,
):
    """Implementación SQLAlchemy del repositorio de artículos de catálogo."""

    def __init__(
        self,
        session: AsyncSession,
        pending_events: list[DomainEvent] | None = None,
    ) -> None:
        super().__init__(
            session,
            CatalogArticleModel,
            pending_events,
        )

    def _to_model(
        self,
        entity: CatalogArticle,
    ) -> CatalogArticleModel:
        return CatalogArticleModel(
            id=entity.id,
            empresa_id=entity.empresa_id,
            categoria_id=entity.categoria_id,
            nombre=entity.nombre,
            descripcion=entity.descripcion,
            fabricante=entity.fabricante,
            modelo=entity.modelo,
            unidad_medida=entity.unidad_medida,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    def _to_entity(
        self,
        model: CatalogArticleModel,
    ) -> CatalogArticle:
        return CatalogArticle(
            id=model.id,
            empresa_id=model.empresa_id,
            categoria_id=model.categoria_id,
            nombre=model.nombre,
            descripcion=model.descripcion,
            fabricante=model.fabricante,
            modelo=model.modelo,
            unidad_medida=model.unidad_medida,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def list_by_company(
        self,
        empresa_id: CompanyId,
        offset: int,
        limit: int,
        filters: dict[str, Any] | None = None,
    ) -> tuple[list[CatalogArticle], int]:
        stmt = select(CatalogArticleModel).where(
            CatalogArticleModel.empresa_id == empresa_id.value
        )

        count_stmt = select(
            func.count(CatalogArticleModel.id)
        ).where(
            CatalogArticleModel.empresa_id == empresa_id.value
        )

        if filters:
            if filters.get("categoria_id"):
                stmt = stmt.where(
                    CatalogArticleModel.categoria_id
                    == filters["categoria_id"]
                )
                count_stmt = count_stmt.where(
                    CatalogArticleModel.categoria_id
                    == filters["categoria_id"]
                )

            if filters.get("search"):
                search = f"%{filters['search']}%"

                stmt = stmt.where(
                    CatalogArticleModel.nombre.ilike(search)
                )

                count_stmt = count_stmt.where(
                    CatalogArticleModel.nombre.ilike(search)
                )

        count_result = await self.session.execute(
            count_stmt
        )
        total = count_result.scalar_one()

        stmt = (
            stmt.order_by(CatalogArticleModel.nombre)
            .offset(offset)
            .limit(limit)
        )

        result = await self.session.execute(stmt)

        return (
            [self._to_entity(m) for m in result.scalars().all()],
            total,
        )