"""Repositorio de ubicaciones jerárquicas con SQLAlchemy asíncrono."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.location_repository import LocationRepositoryPort
from app.domain.entities import Location
from app.domain.events import DomainEvent
from app.domain.value_objects import CompanyId, LocationId
from app.infrastructure.db.models.location import LocationModel
from app.infrastructure.repositories.tenant_repository import SqlAlchemyTenantRepository


class SqlAlchemyLocationRepository(
    SqlAlchemyTenantRepository[LocationModel, Location, LocationId], LocationRepositoryPort
):
    """Implementación en SQLAlchemy para el puerto de repositorio de Ubicaciones."""

    def __init__(
        self, session: AsyncSession, pending_events: list[DomainEvent] | None = None
    ) -> None:
        super().__init__(session, LocationModel, pending_events)

    def _to_model(self, entity: Location) -> LocationModel:
        return LocationModel(
            id=entity.id.value,
            empresa_id=entity.empresa_id.value,
            parent_id=entity.parent_id.value if entity.parent_id else None,
            nombre=entity.nombre,
            tipo=entity.tipo,
            descripcion=entity.descripcion,
            version=entity.version,
        )

    def _to_entity(self, model: LocationModel) -> Location:
        return Location(
            id=LocationId(model.id),
            empresa_id=CompanyId(model.empresa_id),
            parent_id=LocationId(model.parent_id) if model.parent_id else None,
            nombre=model.nombre,
            tipo=model.tipo,
            descripcion=model.descripcion,
            version=model.version,
        )

    async def get_tree(self, empresa_id: CompanyId) -> list[Location]:
        """Obtiene todos los nodos de ubicación para construir el árbol en memoria.

        Args:
            empresa_id: Identificador de la empresa.

        Returns:
            Lista con todas las ubicaciones registradas para la empresa.
        """
        stmt = select(LocationModel).where(LocationModel.empresa_id == empresa_id.value)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def get_children(self, parent_id: LocationId, empresa_id: CompanyId) -> list[Location]:
        """Obtiene las ubicaciones hijas directas de un nodo padre.

        Args:
            parent_id: Identificador de la ubicación padre.
            empresa_id: Identificador de la empresa.

        Returns:
            Lista de ubicaciones hijas directas.
        """
        stmt = select(LocationModel).where(
            LocationModel.parent_id == parent_id.value,
            LocationModel.empresa_id == empresa_id.value,
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]
