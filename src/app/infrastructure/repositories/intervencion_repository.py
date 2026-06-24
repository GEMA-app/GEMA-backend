"""Repositorio concreto para intervenciones técnicas."""

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.intervencion_repository import IntervencionRepositoryPort
from app.domain.entities.intervencion_tecnica import IntervencionTecnica
from app.domain.value_objects.identifier import CompanyId, IntervencionId, OrdenTrabajoId, UserId
from app.infrastructure.db.models.intervencion import IntervencionModel
from app.infrastructure.repositories.base import SqlAlchemyRepository


class SqlAlchemyIntervencionRepository(
    SqlAlchemyRepository[IntervencionModel, IntervencionTecnica],
    IntervencionRepositoryPort,
):
    """Implementación SQLAlchemy del repositorio de intervenciones."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, IntervencionModel)
        self.pk_column = "id"

    def _to_entity(self, model: IntervencionModel) -> IntervencionTecnica:
        """Convierte un modelo ORM a una entidad de dominio."""
        return IntervencionTecnica(
            id=IntervencionId.from_string(str(model.id)),
            orden_trabajo_id=OrdenTrabajoId.from_string(str(model.orden_trabajo_id)),
            tecnico_id=UserId.from_string(str(model.tecnico_id)),
            descripcion=model.descripcion,
            fecha_inicio=model.fecha_inicio,
            fecha_fin=model.fecha_fin,
            horas_trabajadas=model.horas_trabajadas,
            costo=model.costo,
            estado=model.estado,
            observaciones=model.observaciones,
        )

    def _to_model(self, entity: IntervencionTecnica) -> IntervencionModel:
        """Convierte una entidad de dominio a un modelo ORM."""
        return IntervencionModel(
            id=entity.id.value,
            orden_trabajo_id=entity.orden_trabajo_id.value,
            tecnico_id=entity.tecnico_id.value,
            descripcion=entity.descripcion,
            fecha_inicio=entity.fecha_inicio,
            fecha_fin=entity.fecha_fin,
            horas_trabajadas=entity.horas_trabajadas,
            costo=entity.costo,
            estado=entity.estado,
            observaciones=entity.observaciones,
        )

    async def get_by_orden_trabajo(
        self,
        orden_trabajo_id: OrdenTrabajoId,
        empresa_id: CompanyId,
    ) -> list[IntervencionTecnica]:
        """Obtiene todas las intervenciones de una orden de trabajo."""
        stmt = (
            select(IntervencionModel)
            .where(IntervencionModel.orden_trabajo_id == orden_trabajo_id.value)
            .where(IntervencionModel.empresa_id == empresa_id.value)
            .order_by(IntervencionModel.fecha_inicio.desc())
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def get_by_tecnico(
        self,
        tecnico_id: UserId,
        empresa_id: CompanyId,
    ) -> list[IntervencionTecnica]:
        """Obtiene todas las intervenciones realizadas por un técnico."""
        stmt = (
            select(IntervencionModel)
            .where(IntervencionModel.tecnico_id == tecnico_id.value)
            .where(IntervencionModel.empresa_id == empresa_id.value)
            .order_by(IntervencionModel.fecha_inicio.desc())
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def list(
        self,
        empresa_id: CompanyId,
        offset: int = 0,
        limit: int = 100,
    ) -> tuple[list[IntervencionTecnica], int]:
        """Lista todas las intervenciones de una empresa con paginación."""
        # Consulta de conteo
        count_stmt = select(IntervencionModel).where(IntervencionModel.empresa_id == empresa_id.value)
        count_result = await self._session.execute(count_stmt)
        total = len(count_result.scalars().all())

        # Consulta de datos
        stmt = (
            select(IntervencionModel)
            .where(IntervencionModel.empresa_id == empresa_id.value)
            .order_by(IntervencionModel.fecha_inicio.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [self._to_entity(m) for m in models], total