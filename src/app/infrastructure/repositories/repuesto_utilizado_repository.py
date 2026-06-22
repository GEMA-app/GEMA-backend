# src/app/infrastructure/repositories/repuesto_utilizado_repository.py
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.repuesto_utilizado_repository import RepuestoUtilizadoRepositoryPort
from app.domain.entities.repuesto_utilizado import RepuestoUtilizado
from app.domain.value_objects import CompanyId, InterventionId, RepuestoId
from app.infrastructure.db.models.repuesto_utilizado import RepuestoUtilizadoModel
from app.infrastructure.repositories.base import SqlAlchemyRepository


class SqlAlchemyRepuestoUtilizadoRepository(
    SqlAlchemyRepository[RepuestoUtilizadoModel, RepuestoUtilizado],
    RepuestoUtilizadoRepositoryPort,
):
    """Implementación concreta del repositorio de repuestos utilizados usando SQLAlchemy."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, RepuestoUtilizadoModel)
        self.pk_column = "id"

    def _to_entity(self, model: RepuestoUtilizadoModel) -> RepuestoUtilizado:
        """Convierte un modelo ORM a una entidad de dominio."""
        return RepuestoUtilizado(
            id=model.id,
            empresa_id=CompanyId(model.empresa_id),
            intervencion_id=InterventionId(model.intervencion_id),
            repuesto_id=RepuestoId(model.repuesto_id),
            cantidad_usada=model.cantidad_usada,
            precio_unitario=model.precio_unitario,
            moneda=model.moneda,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: RepuestoUtilizado) -> RepuestoUtilizadoModel:
        """Convierte una entidad de dominio a un modelo ORM."""
        return RepuestoUtilizadoModel(
            id=entity.id,
            empresa_id=entity.empresa_id.value,
            intervencion_id=entity.intervencion_id.value,
            repuesto_id=entity.repuesto_id.value,
            cantidad_usada=entity.cantidad_usada,
            precio_unitario=entity.precio_unitario,
            moneda=entity.moneda,
        )

    async def get_by_intervention(
        self, company_id: CompanyId, intervention_id: InterventionId
    ) -> list[RepuestoUtilizado]:
        """Lista todos los repuestos utilizados en una intervención específica."""
        stmt = (
            select(self.model)
            .where(self.model.empresa_id == company_id.value)
            .where(self.model.intervencion_id == intervention_id.value)
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]