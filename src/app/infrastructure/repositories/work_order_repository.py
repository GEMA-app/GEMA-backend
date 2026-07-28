"""Adaptador SQLAlchemy del repositorio de órdenes de trabajo.

Implementa el puerto WorkOrderRepositoryPort usando SQLAlchemy 2.0
con sesión asíncrona.
"""

import uuid

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dtos.work_order_dtos import WorkOrderStatusLogResponse
from app.application.ports.work_order_repository import WorkOrderRepositoryPort
from app.domain.entities import WorkOrder
from app.domain.enums import MaintenanceType, WorkOrderStatus
from app.domain.events import DomainEvent
from app.domain.value_objects import AssetId, CompanyId, UserId, WorkOrderId
from app.infrastructure.db.models.work_order import WorkOrderModel
from app.infrastructure.repositories.tenant_repository import SqlAlchemyTenantRepository


class SqlAlchemyWorkOrderRepository(
    SqlAlchemyTenantRepository[WorkOrderModel, WorkOrder, WorkOrderId],
    WorkOrderRepositoryPort,
):
    """Repositorio SQLAlchemy para órdenes de trabajo.

    Implementa las operaciones de persistencia usando el repositorio
    genérico SqlAlchemyRepository y añade métodos específicos como
    búsqueda por código y listado con filtros.
    """

    pk_column = "id"

    def __init__(
        self, session: AsyncSession, pending_events: list[DomainEvent] | None = None
    ) -> None:
        super().__init__(session, WorkOrderModel, pending_events)

    def _to_model(self, entity: WorkOrder) -> WorkOrderModel:
        """Convierte una entidad WorkOrder a modelo ORM."""
        return WorkOrderModel(
            id=entity.id.value,
            empresa_id=entity.empresa_id.value,
            codigo_ot=entity.codigo_ot,
            activo_id=entity.activo_id.value,
            reporte_id=uuid.UUID(entity.reporte_id) if entity.reporte_id else None,
            plan_id=uuid.UUID(entity.plan_id) if entity.plan_id else None,
            supervisor_id=entity.supervisor_id.value if entity.supervisor_id else None,
            tipo=entity.tipo,
            estado=entity.estado,
            fecha_apertura=entity.fecha_apertura,
            fecha_inicio_trabajo=entity.fecha_inicio_trabajo,
            fecha_cierre=entity.fecha_cierre,
            descripcion_trabajo=entity.descripcion_trabajo,
            costo_estimado=entity.costo_estimado,
            costo_real=entity.costo_real,
            moneda=entity.moneda,
            validado_por_id=entity.validado_por_id.value if entity.validado_por_id else None,
            fecha_validacion=entity.fecha_validacion,
        )

    def _to_entity(self, model: WorkOrderModel) -> WorkOrder:
        """Convierte un modelo ORM a entidad WorkOrder."""
        return WorkOrder(
            id=WorkOrderId(model.id),
            empresa_id=CompanyId(model.empresa_id),
            codigo_ot=model.codigo_ot,
            activo_id=AssetId(model.activo_id),
            reporte_id=str(model.reporte_id) if model.reporte_id else None,
            plan_id=str(model.plan_id) if model.plan_id else None,
            supervisor_id=UserId(model.supervisor_id) if model.supervisor_id else None,
            tipo=model.tipo,
            estado=model.estado,
            fecha_apertura=model.fecha_apertura,
            fecha_inicio_trabajo=model.fecha_inicio_trabajo,
            fecha_cierre=model.fecha_cierre,
            descripcion_trabajo=model.descripcion_trabajo,
            costo_estimado=(
                float(model.costo_estimado) if model.costo_estimado is not None else None
            ),
            costo_real=float(model.costo_real) if model.costo_real is not None else None,
            moneda=model.moneda,
            validado_por_id=UserId(model.validado_por_id) if model.validado_por_id else None,
            fecha_validacion=model.fecha_validacion,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def get_by_code(self, codigo_ot: str, empresa_id: CompanyId) -> WorkOrder | None:
        """Obtiene una orden de trabajo por su código único dentro de la empresa.

        Returns:
            La entidad WorkOrder si existe, None en caso contrario.
        """
        stmt = select(WorkOrderModel).where(
            WorkOrderModel.codigo_ot == codigo_ot,
            WorkOrderModel.empresa_id == empresa_id.value,
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_by_company(
        self,
        empresa_id: CompanyId,
        estado: str | None = None,
        activo_id: AssetId | None = None,
        tipo: str | None = None,
        supervisor_id: str | None = None,
        tecnico_id: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[WorkOrder], int]:
        """Lista órdenes de trabajo de una empresa con filtros opcionales.

        Returns:
            Tupla con la lista de órdenes de trabajo y el total de registros.
        """
        stmt = select(WorkOrderModel).where(WorkOrderModel.empresa_id == empresa_id.value)
        count_stmt = select(func.count(WorkOrderModel.id)).where(
            WorkOrderModel.empresa_id == empresa_id.value
        )
        if estado:
            stmt = stmt.where(WorkOrderModel.estado == WorkOrderStatus(estado))
            count_stmt = count_stmt.where(WorkOrderModel.estado == WorkOrderStatus(estado))
        if activo_id:
            stmt = stmt.where(WorkOrderModel.activo_id == activo_id.value)
            count_stmt = count_stmt.where(WorkOrderModel.activo_id == activo_id.value)
        if tipo:
            stmt = stmt.where(WorkOrderModel.tipo == MaintenanceType(tipo))
            count_stmt = count_stmt.where(WorkOrderModel.tipo == MaintenanceType(tipo))
        if supervisor_id:
            stmt = stmt.where(WorkOrderModel.supervisor_id == uuid.UUID(supervisor_id))
            count_stmt = count_stmt.where(WorkOrderModel.supervisor_id == uuid.UUID(supervisor_id))
        if tecnico_id:
            from app.infrastructure.db.models.work_order import WorkOrderTechnicianModel
            stmt = stmt.join(
                WorkOrderTechnicianModel,
                WorkOrderModel.id == WorkOrderTechnicianModel.ordenes_trabajo_id,
            ).where(WorkOrderTechnicianModel.tecnico_id == uuid.UUID(tecnico_id))
            count_stmt = count_stmt.join(
                WorkOrderTechnicianModel,
                WorkOrderModel.id == WorkOrderTechnicianModel.ordenes_trabajo_id,
            ).where(WorkOrderTechnicianModel.tecnico_id == uuid.UUID(tecnico_id))
        stmt = stmt.order_by(WorkOrderModel.created_at.desc())
        stmt = stmt.offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        entities = [self._to_entity(m) for m in models]
        total_res = await self.session.execute(count_stmt)
        total = total_res.scalar() or 0
        return entities, total

    async def get_by_report_id(self, reporte_id: str, empresa_id: CompanyId) -> WorkOrder | None:
        """Obtiene una orden de trabajo asociada a un reporte de falla.

        Returns:
            La entidad WorkOrder si existe, None en caso contrario.
        """
        stmt = select(WorkOrderModel).where(
            WorkOrderModel.reporte_id == uuid.UUID(reporte_id),
            WorkOrderModel.empresa_id == empresa_id.value,
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def assign_technician(
        self, id: WorkOrderId, technician_id: UserId, empresa_id: CompanyId
    ) -> None:
        """Asigna un técnico a una orden de trabajo si no está ya asignado."""
        from app.infrastructure.db.models.work_order import WorkOrderTechnicianModel

        stmt = select(WorkOrderTechnicianModel).where(
            WorkOrderTechnicianModel.ordenes_trabajo_id == id.value,
            WorkOrderTechnicianModel.tecnico_id == technician_id.value,
        )
        res = await self.session.execute(stmt)
        existing = res.scalar_one_or_none()
        if not existing:
            assoc = WorkOrderTechnicianModel(
                empresa_id=empresa_id.value,
                ordenes_trabajo_id=id.value,
                tecnico_id=technician_id.value,
            )
            self.session.add(assoc)

    async def remove_technician(
        self, id: WorkOrderId, technician_id: UserId, empresa_id: CompanyId
    ) -> None:
        """Remueve un técnico de una orden de trabajo."""
        from app.infrastructure.db.models.work_order import WorkOrderTechnicianModel

        stmt = delete(WorkOrderTechnicianModel).where(
            WorkOrderTechnicianModel.ordenes_trabajo_id == id.value,
            WorkOrderTechnicianModel.tecnico_id == technician_id.value,
            WorkOrderTechnicianModel.empresa_id == empresa_id.value,
        )
        await self.session.execute(stmt)

    async def add_status_log(
        self,
        id: WorkOrderId,
        previous_status: WorkOrderStatus | None,
        new_status: WorkOrderStatus,
        usuario_id: UserId | None,
        motivo: str,
        empresa_id: CompanyId,
    ) -> None:
        """Registra un cambio de estado en el historial de base de datos."""
        from datetime import UTC, datetime

        from app.infrastructure.db.models.work_order import WorkOrderStatusLogModel

        log_entry = WorkOrderStatusLogModel(
            id=uuid.uuid4(),
            empresa_id=empresa_id.value,
            ordenes_trabajo_id=id.value,
            estado_anterior=previous_status,
            estado_nuevo=new_status,
            usuario_id=usuario_id.value if usuario_id else None,
            motivo=motivo,
            fecha_cambio=datetime.now(UTC),
        )
        self.session.add(log_entry)

    async def get_status_history(
        self, id: WorkOrderId, empresa_id: CompanyId
    ) -> list[WorkOrderStatusLogResponse]:
        """Obtiene la lista de cambios de estado de una OT."""
        from app.application.dtos.work_order_dtos import WorkOrderStatusLogResponse
        from app.infrastructure.db.models.work_order import WorkOrderStatusLogModel

        stmt = (
            select(WorkOrderStatusLogModel)
            .where(
                WorkOrderStatusLogModel.ordenes_trabajo_id == id.value,
                WorkOrderStatusLogModel.empresa_id == empresa_id.value,
            )
            .order_by(WorkOrderStatusLogModel.fecha_cambio.asc())
        )

        res = await self.session.execute(stmt)
        models = res.scalars().all()
        return [
            WorkOrderStatusLogResponse(
                id=str(m.id),
                ordenes_trabajo_id=str(m.ordenes_trabajo_id),
                estado_anterior=m.estado_anterior.value if m.estado_anterior else None,
                estado_nuevo=m.estado_nuevo.value,
                usuario_id=str(m.usuario_id) if m.usuario_id else None,
                motivo=m.motivo,
                fecha_cambio=m.fecha_cambio,
            )
            for m in models
        ]
