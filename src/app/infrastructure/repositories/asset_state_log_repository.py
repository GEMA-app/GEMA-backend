"""Repositorio de AssetStateLog con SQLAlchemy asíncrono."""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.asset_state_log_repository import AssetStateLogRepositoryPort
from app.domain.entities.asset_state_log import AssetStateLog
from app.domain.events import DomainEvent
from app.domain.value_objects.identifier import AssetId, CompanyId
from app.infrastructure.db.models.asset_state_log import AssetStateLogModel
from app.infrastructure.repositories.tenant_repository import SqlAlchemyTenantRepository

if TYPE_CHECKING:
    pass


class SqlAlchemyAssetStateLogRepository(
    SqlAlchemyTenantRepository[AssetStateLogModel, AssetStateLog, uuid.UUID],
    AssetStateLogRepositoryPort,
):
    """Implementación en SQLAlchemy para el puerto de repositorio de AssetStateLog."""

    def __init__(
        self,
        session: AsyncSession,
        pending_events: list[DomainEvent] | None = None,
    ) -> None:
        super().__init__(session, AssetStateLogModel, pending_events)

    async def list_by_asset(
        self, activo_id: AssetId, empresa_id: CompanyId
    ) -> list[AssetStateLog]:
        """Lista los cambios de estado de un activo ordenados del más reciente al más antiguo.

        Args:
            activo_id: Identificador del activo.
            empresa_id: Identificador de la empresa (tenant).

        Returns:
            Lista de entidades AssetStateLog.
        """
        stmt = (
            select(AssetStateLogModel)
            .where(
                AssetStateLogModel.activo_id == activo_id.value,
                AssetStateLogModel.empresa_id == empresa_id.value,
            )
            .order_by(AssetStateLogModel.fecha_cambio.desc())
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    def _to_model(self, entity: AssetStateLog) -> AssetStateLogModel:
        return AssetStateLogModel(
            id=entity.id,
            empresa_id=entity.empresa_id.value,
            activo_id=entity.activo_id.value,
            usuario_id=entity.usuario_id,
            estado_anterior=entity.estado_anterior,
            estado_nuevo=entity.estado_nuevo,
            motivo=entity.motivo,
            fecha_cambio=entity.fecha_cambio,
            version=entity.version,
        )

    def _to_entity(self, model: AssetStateLogModel) -> AssetStateLog:
        return AssetStateLog(
            id=model.id,
            empresa_id=CompanyId(model.empresa_id),
            activo_id=AssetId(model.activo_id),
            usuario_id=model.usuario_id,
            estado_anterior=model.estado_anterior,
            estado_nuevo=model.estado_nuevo,
            motivo=model.motivo,
            fecha_cambio=model.fecha_cambio,
            version=model.version,
        )
