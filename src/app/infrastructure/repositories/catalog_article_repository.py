"""Repositorio SQLAlchemy para artículos de catálogo."""

import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.catalog_article_repository import (
    CatalogArticleRepositoryPort,
)
from app.domain.entities import CatalogArticle
from app.domain.events import DomainEvent
from app.domain.value_objects import CompanyId
from app.infrastructure.db.models.catalog_article import CatalogArticleModel
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
    """Implementación SQLAlchemy del repositorio de artículos de catálogo.

    Esta implementación concreta traduce entre la entidad de dominio
    ``CatalogArticle`` y el modelo ORM ``CatalogArticleModel``.
    """

    def __init__(
        self,
        session: AsyncSession,
        pending_events: list[DomainEvent] | None = None,
    ) -> None:
        """Inicializa el repositorio con una sesión de base de datos.

        Args:
            session: Sesión asíncrona de SQLAlchemy.
            pending_events: Lista opcional para acumular eventos de dominio.
        """
        super().__init__(
            session,
            CatalogArticleModel,
            pending_events,
        )

    def _to_model(
        self,
        entity: CatalogArticle,
    ) -> CatalogArticleModel:
        """Convierte una entidad de dominio a modelo ORM."""
        return CatalogArticleModel(
            id=entity.id,
            empresa_id=entity.empresa_id,
            category_id=entity.category_id,
            name=entity.name,
            description=entity.description,
            manufacturer=entity.manufacturer,
            model=entity.model,
            unit_of_measure=entity.unit_of_measure,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    def _to_entity(
        self,
        model: CatalogArticleModel,
    ) -> CatalogArticle:
        """Convierte un modelo ORM a entidad de dominio."""
        return CatalogArticle(
            id=model.id,
            empresa_id=model.empresa_id,
            category_id=model.category_id,
            name=model.name,
            description=model.description,
            manufacturer=model.manufacturer,
            model=model.model,
            unit_of_measure=model.unit_of_measure,
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
        """Lista artículos de una empresa con paginación y filtros opcionales.

        Args:
            empresa_id: Identificador de la empresa.
            offset: Número de registros a saltar.
            limit: Máximo de registros a retornar.
            filters: Diccionario opcional de filtros.
                Claves soportadas: "category_id" (UUID), "search" (str).

        Returns:
            Tupla con la lista de artículos y el total de registros sin paginación.
        """
        stmt = select(CatalogArticleModel).where(CatalogArticleModel.empresa_id == empresa_id.value)

        count_stmt = select(func.count(CatalogArticleModel.id)).where(
            CatalogArticleModel.empresa_id == empresa_id.value
        )

        if filters:
            if filters.get("category_id"):
                stmt = stmt.where(CatalogArticleModel.category_id == filters["category_id"])
                count_stmt = count_stmt.where(
                    CatalogArticleModel.category_id == filters["category_id"]
                )

            if filters.get("search"):
                search = f"%{filters['search']}%"

                stmt = stmt.where(CatalogArticleModel.name.ilike(search))

                count_stmt = count_stmt.where(CatalogArticleModel.name.ilike(search))

        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar_one()

        stmt = stmt.order_by(CatalogArticleModel.name).offset(offset).limit(limit)

        result = await self.session.execute(stmt)

        return (
            [self._to_entity(m) for m in result.scalars().all()],
            total,
        )

    async def get_by_company_and_id(
        self,
        article_id: uuid.UUID,
        empresa_id: CompanyId,
    ) -> CatalogArticle | None:
        """Obtiene un artículo por ID verificando que pertenezca a la empresa.

        Args:
            article_id: Identificador UUID del artículo.
            empresa_id: Identificador de la empresa.

        Returns:
            El artículo si existe y pertenece a la empresa, o None.
        """
        stmt = select(CatalogArticleModel).where(
            CatalogArticleModel.id == article_id,
            CatalogArticleModel.empresa_id == empresa_id.value,
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def exists_by_company_id(
        self,
        article_id: uuid.UUID,
    ) -> bool:
        """Verifica si existe un artículo de catálogo por su ID.

        Args:
            article_id: Identificador UUID del artículo.

        Returns:
            True si el artículo existe, False en caso contrario.
        """
        stmt = select(CatalogArticleModel.id).where(CatalogArticleModel.id == article_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None
