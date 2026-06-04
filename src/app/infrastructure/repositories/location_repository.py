
from sqlalchemy import delete as sql_delete
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.location_repository import LocationRepositoryPort
from app.domain.entities import Location
from app.domain.value_objects import CompanyId, LocationId
from app.infrastructure.db.models.location import LocationModel
from app.infrastructure.repositories.base import SqlAlchemyRepository


class SqlAlchemyLocationRepository(SqlAlchemyRepository[LocationModel, Location, LocationId], LocationRepositoryPort):
    """Implementación en SQLAlchemy para el puerto de repositorio de Ubicaciones."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, LocationModel)

    def _to_model(self, entity: Location) -> LocationModel:
        return LocationModel(
            id=entity.id.value,
            empresa_id=entity.empresa_id.value,
            parent_id=entity.parent_id.value if entity.parent_id else None,
            nombre=entity.nombre,
            tipo=entity.tipo,
            descripcion=entity.descripcion
        )

    def _to_entity(self, model: LocationModel) -> Location:
        return Location(
            id=LocationId(model.id),
            empresa_id=CompanyId(model.empresa_id),
            parent_id=LocationId(model.parent_id) if model.parent_id else None,
            nombre=model.nombre,
            tipo=model.tipo,
            descripcion=model.descripcion
        )

    async def get_by_id(self, id: LocationId, empresa_id: CompanyId) -> Location | None:  # type: ignore[override]
        stmt = select(LocationModel).where(
            LocationModel.id == id.value,
            LocationModel.empresa_id == empresa_id.value
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_entity(model)

    async def get_tree(self, empresa_id: CompanyId) -> list[Location]:
        # Para obtener el árbol completo de la empresa, consultamos todos sus nodos.
        # Luego la jerarquía se construye en memoria en la capa de aplicación o presentación.
        stmt = select(LocationModel).where(LocationModel.empresa_id == empresa_id.value)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def get_children(self, parent_id: LocationId, empresa_id: CompanyId) -> list[Location]:
        stmt = select(LocationModel).where(
            LocationModel.parent_id == parent_id.value,
            LocationModel.empresa_id == empresa_id.value
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def delete(self, id: LocationId, empresa_id: CompanyId) -> None:  # type: ignore[override]
        stmt = sql_delete(LocationModel).where(
            LocationModel.id == id.value,
            LocationModel.empresa_id == empresa_id.value
        )
        await self.session.execute(stmt)
