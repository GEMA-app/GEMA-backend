from typing import Any

from sqlalchemy import delete as sql_delete
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.asset_repository import AssetRepositoryPort
from app.domain.entities import Asset
from app.domain.value_objects import AssetId, CompanyId, LocationId
from app.infrastructure.db.models.asset import AssetModel
from app.infrastructure.repositories.base import SqlAlchemyRepository


class SqlAlchemyAssetRepository(
    SqlAlchemyRepository[AssetModel, Asset, AssetId], AssetRepositoryPort
):
    """Implementación en SQLAlchemy para el puerto de repositorio de Activos."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, AssetModel)

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
            valor_monetario=float(model.valor_monetario)
            if model.valor_monetario is not None
            else None,
            moneda=model.moneda,
        )

    async def get_by_id(self, id: AssetId, empresa_id: CompanyId) -> Asset | None:  # type: ignore[override]
        stmt = select(AssetModel).where(
            AssetModel.id == id.value, AssetModel.empresa_id == empresa_id.value
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_entity(model)

    async def list_by_company(
        self, empresa_id: CompanyId, offset: int, limit: int, filters: dict[str, Any] | None = None
    ) -> tuple[list[Asset], int]:
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

        stmt = stmt.offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models], total

    async def delete(self, id: AssetId, empresa_id: CompanyId) -> None:  # type: ignore[override]
        stmt = sql_delete(AssetModel).where(
            AssetModel.id == id.value, AssetModel.empresa_id == empresa_id.value
        )
        await self.session.execute(stmt)
