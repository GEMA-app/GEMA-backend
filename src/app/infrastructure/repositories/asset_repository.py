"""Repositorio de activos físicos con SQLAlchemy asíncrono."""

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.asset_repository import AssetRepositoryPort
from app.domain.entities import Asset
from app.domain.events import DomainEvent
from app.domain.value_objects import AssetId, CompanyId, LocationId
from app.infrastructure.db.models.asset import AssetModel
from app.infrastructure.repositories.tenant_repository import SqlAlchemyTenantRepository


class SqlAlchemyAssetRepository(
    SqlAlchemyTenantRepository[AssetModel, Asset, AssetId], AssetRepositoryPort
):
    """Implementación en SQLAlchemy para el puerto de repositorio de Activos."""

    def __init__(
        self, session: AsyncSession, pending_events: list[DomainEvent] | None = None
    ) -> None:
        super().__init__(session, AssetModel, pending_events)

    def _to_model(self, entity: Asset) -> AssetModel:
        return AssetModel(
            id=entity.id.value,
            empresa_id=entity.empresa_id.value,
            articulo_id=entity.articulo_id,
            ubicacion_id=entity.ubicacion_id.value if entity.ubicacion_id else None,
            serial_interno=entity.serial_interno,
            codigo_activo=entity.codigo_activo,
            estado=entity.estado,
            fecha_adquisicion=entity.fecha_adquisicion,
            valor_monetario=entity.valor_monetario,
            moneda=entity.moneda,
            version=entity.version,
        )

    def _to_entity(self, model: AssetModel) -> Asset:
        return Asset(
            id=AssetId(model.id),
            empresa_id=CompanyId(model.empresa_id),
            articulo_id=model.articulo_id,
            ubicacion_id=LocationId(model.ubicacion_id) if model.ubicacion_id else None,
            serial_interno=model.serial_interno,
            codigo_activo=model.codigo_activo,
            estado=model.estado,
            fecha_adquisicion=model.fecha_adquisicion,
            valor_monetario=model.valor_monetario,
            moneda=model.moneda,
            version=model.version,
        )

    async def list_by_company(
        self, empresa_id: CompanyId, offset: int, limit: int, filters: dict[str, Any] | None = None
    ) -> tuple[list[Asset], int]:
        """Lista los activos de una empresa con soporte de filtros y paginación.

        Args:
            empresa_id: Identificador de la empresa.
            offset: Número de registros a omitir.
            limit: Número máximo de registros a retornar.
            filters: Diccionario opcional con filtros de búsqueda (estado, ubicacion_id, search).

        Returns:
            Una tupla con la lista de entidades de tipo Asset encontradas y el conteo total.
        """
        from sqlalchemy import func

        stmt = select(AssetModel).where(AssetModel.empresa_id == empresa_id.value)
        count_stmt = select(func.count(AssetModel.id)).where(
            AssetModel.empresa_id == empresa_id.value
        )

        if filters:
            if "estado" in filters and filters["estado"]:
                stmt = stmt.where(AssetModel.estado == filters["estado"])
                count_stmt = count_stmt.where(AssetModel.estado == filters["estado"])
            if "ubicacion_id" in filters and filters["ubicacion_id"]:
                stmt = stmt.where(AssetModel.ubicacion_id == filters["ubicacion_id"])
                count_stmt = count_stmt.where(AssetModel.ubicacion_id == filters["ubicacion_id"])
            if "search" in filters and filters["search"]:
                search_term = f"%{filters['search']}%"
                stmt = stmt.where(
                    AssetModel.codigo_activo.ilike(search_term)
                    | AssetModel.serial_interno.ilike(search_term)
                )
                count_stmt = count_stmt.where(
                    AssetModel.codigo_activo.ilike(search_term)
                    | AssetModel.serial_interno.ilike(search_term)
                )

        count_res = await self.session.execute(count_stmt)
        total = count_res.scalar_one()

        stmt = stmt.offset(offset).limit(limit).order_by(AssetModel.id)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models], total
