"""Implementación SQLAlchemy del repositorio de UsedPart."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.used_part_repository import UsedPartRepositoryPort
from app.domain.entities.used_part import UsedPart
from app.domain.events import DomainEvent
from app.domain.value_objects import CompanyId, InterventionId
from app.infrastructure.db.models.used_part import UsedPartModel
from app.infrastructure.repositories.tenant_repository import SqlAlchemyTenantRepository


class SqlAlchemyUsedPartRepository(
    SqlAlchemyTenantRepository[UsedPartModel, UsedPart, UUID],
    UsedPartRepositoryPort,
):
    """Implementación concreta del repositorio de repuestos utilizados usando SQLAlchemy."""

    def __init__(
        self, session: AsyncSession, pending_events: list[DomainEvent] | None = None
    ) -> None:
        super().__init__(session, UsedPartModel, pending_events)
        self.pk_column = "id"

    def _to_entity(self, model: UsedPartModel) -> UsedPart:
        """Convierte un modelo ORM a una entidad de dominio.

        Args:
            model: Modelo ORM de UsedPart.

        Returns:
            Entidad de dominio UsedPart.
        """
        return UsedPart(
            id=model.id,
            empresa_id=CompanyId(model.empresa_id),
            intervencion_id=model.intervencion_id,
            repuesto_id=model.repuesto_id,
            cantidad_usada=model.cantidad_usada,
            precio_unitario=model.precio_unitario,
            moneda=model.moneda,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: UsedPart) -> UsedPartModel:
        """Convierte una entidad de dominio a un modelo ORM.

        Args:
            entity: Entidad de dominio UsedPart.

        Returns:
            Modelo ORM UsedPartModel.
        """
        return UsedPartModel(
            id=entity.id,
            empresa_id=entity.empresa_id.value,
            intervencion_id=entity.intervencion_id,
            repuesto_id=entity.repuesto_id,
            cantidad_usada=entity.cantidad_usada,
            precio_unitario=entity.precio_unitario,
            moneda=entity.moneda,
        )

    async def get_by_intervention(
        self, company_id: CompanyId, intervention_id: InterventionId
    ) -> list[UsedPart]:
        """Lista todos los repuestos utilizados en una intervención específica.

        Args:
            company_id: Identificador de la empresa (tenant).
            intervention_id: Identificador de la intervención.

        Returns:
            Lista de entidades UsedPart.
        """
        stmt = (
            select(self.model_class)
            .where(self.model_class.empresa_id == company_id.value)
            .where(self.model_class.intervencion_id == intervention_id.value)
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]
