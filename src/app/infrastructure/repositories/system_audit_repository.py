from typing import Any

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.system_audit_repository import SystemAuditRepositoryPort
from app.domain.entities.system_audit import SystemAudit as SystemAuditEntity
from app.domain.events import DomainEvent
from app.domain.value_objects import CompanyId, UserId
from app.infrastructure.db.models.system_audits import SystemAuditModel
from app.infrastructure.repositories.base import SqlAlchemyRepository


class SqlAlchemySystemAuditRepository(
    SqlAlchemyRepository[SystemAuditModel, SystemAuditEntity, int],
    SystemAuditRepositoryPort,
):
    """Implementación asíncrona en SQLAlchemy para el puerto de Auditorías de Sistema."""

    pk_column = "id"

    def __init__(
        self, session: AsyncSession, pending_events: list[DomainEvent] | None = None
    ) -> None:
        super().__init__(session, SystemAuditModel, pending_events)

    def _to_model(self, entity: SystemAuditEntity) -> SystemAuditModel:
        """Convierte una entidad de dominio a modelo ORM."""
        return SystemAuditModel(
            id=entity.id,
            empresa_id=entity.empresa_id.value,
            usuario_id=entity.usuario_id.value if entity.usuario_id else None,
            accion=entity.accion,
            detalles=entity.detalles,
            ip_address=entity.ip_address,
            ocurrido_en=entity.ocurrido_en,
        )

    def _to_entity(self, model: SystemAuditModel) -> SystemAuditEntity:
        """Convierte un modelo ORM a entidad de dominio."""
        return SystemAuditEntity(
            id=model.id,
            empresa_id=CompanyId(model.empresa_id),
            usuario_id=UserId.from_string(str(model.usuario_id)) if model.usuario_id else None,
            accion=model.accion,
            detalles=model.detalles,
            ip_address=model.ip_address,
            ocurrido_en=model.ocurrido_en,
        )

    async def get_by_id(self, company_id: CompanyId, audit_id: int) -> SystemAuditEntity | None:  # type: ignore[override]
        """Obtiene una auditoría por ID con ámbito de tenant.

        Args:
            company_id: Identificador del tenant.
            audit_id: ID numérico del registro de auditoría.

        Returns:
            La entidad de dominio si existe, None en caso contrario.
        """
        stmt = select(SystemAuditModel).where(
            SystemAuditModel.empresa_id == company_id.value,
            SystemAuditModel.id == audit_id,
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_all_by_company(
        self,
        company_id: CompanyId,
        offset: int,
        limit: int,
        filters: dict[str, Any],
    ) -> tuple[list[SystemAuditEntity], int]:
        """Obtiene las auditorías filtradas y paginadas de forma asíncrona.

        Args:
            company_id: Identificador del tenant.
            offset: Número de registros a saltar.
            limit: Máximo de registros por página.
            filters: Diccionario con filtros opcionales (usuario_id, accion, fechas).

        Returns:
            Tupla con la lista de entidades y el total de registros sin paginación.
        """
        stmt = select(SystemAuditModel).where(
            SystemAuditModel.empresa_id == company_id.value
        )

        if filters.get("usuario_id") is not None:
            stmt = stmt.where(SystemAuditModel.usuario_id == filters["usuario_id"])
        if filters.get("accion"):
            stmt = stmt.where(SystemAuditModel.accion == filters["accion"])
        if filters.get("fecha_inicio"):
            stmt = stmt.where(
                SystemAuditModel.ocurrido_en >= filters["fecha_inicio"]
            )
        if filters.get("fecha_fin"):
            stmt = stmt.where(
                SystemAuditModel.ocurrido_en <= filters["fecha_fin"]
            )

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar_one()

        stmt = (
            stmt.order_by(desc(SystemAuditModel.ocurrido_en))
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [self._to_entity(m) for m in models], total
