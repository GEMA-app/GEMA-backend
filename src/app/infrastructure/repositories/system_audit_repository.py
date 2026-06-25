from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.system_audit_repository import SystemAuditRepositoryPort
from app.domain.entities.system_audit import SystemAudit as SystemAuditEntity
from app.domain.events import DomainEvent
from app.domain.value_objects import CompanyId, UserId
from app.infrastructure.db.models.system_audits import SystemAudit as SystemAuditModel
from app.infrastructure.repositories.base import SqlAlchemyRepository


class SqlAlchemySystemAuditRepository(
    SqlAlchemyRepository[SystemAuditModel, SystemAuditEntity, int],
    SystemAuditRepositoryPort,
):
    """Implementación asíncrona en SQLAlchemy para el puerto de Auditorías de Sistema."""
    
    pk_column = "id"  # Define que la PK de este modelo es la estándar ("id")

    def __init__(
        self, session: AsyncSession, pending_events: list[DomainEvent] | None = None
    ) -> None:
        super().__init__(session, SystemAuditModel, pending_events)

    def _to_model(self, entity: SystemAuditEntity) -> SystemAuditModel:
        """Mapeo: Traduce una Entidad de Dominio pura a un Modelo ORM de SQLAlchemy."""
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
        """Mapeo: Traduce un Modelo ORM de SQLAlchemy a una Entidad de Dominio pura."""
        return SystemAuditEntity(
            id=model.id,
            empresa_id=CompanyId(model.empresa_id),
            usuario_id=UserId(model.usuario_id) if model.usuario_id else None,
            accion=model.accion,
            detalles=model.detalles,
            ip_address=model.ip_address,
            ocurrido_en=model.ocurrido_en,
        )

    async def get_all_by_empresa(
        self, 
        empresa_id: CompanyId, 
        offset: int, 
        limit: int, 
        filters: Dict[str, Any]
    ) -> Tuple[List[SystemAuditEntity], int]:
        """Obtiene las auditorías filtradas y paginadas de forma asíncrona."""
        
        # 1. Construir la query base filtrando por empresa obligatoriamente
        stmt = select(SystemAuditModel).where(SystemAuditModel.empresa_id == empresa_id.value)
        
        # 2. Aplicar los filtros dinámicos si existen
        if "usuario_id" in filters and filters["usuario_id"] is not None:
            stmt = stmt.where(SystemAuditModel.usuario_id == filters["usuario_id"])
        if "accion" in filters and filters["accion"]:
            stmt = stmt.where(SystemAuditModel.accion == filters["accion"])
        if "fecha_inicio" in filters and filters["fecha_inicio"]:
            stmt = stmt.where(SystemAuditModel.ocurrido_en >= filters["fecha_inicio"])
        if "fecha_fin" in filters and filters["fecha_fin"]:
            stmt = stmt.where(SystemAuditModel.ocurrido_en <= filters["fecha_fin"])

        # 3. Clonar la estructura de filtros para calcular el conteo total (meta-paginación)
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar_one()

        # 4. Aplicar orden descendente por fecha, paginación y ejecutar
        stmt = stmt.order_by(desc(SystemAuditModel.ocurrido_en)).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        models = result.scalars().all()

        # 5. Mapear la lista de modelos ORM a entidades puras de dominio
        entities = [self._to_entity(m) for m in models]
        
        return entities, total