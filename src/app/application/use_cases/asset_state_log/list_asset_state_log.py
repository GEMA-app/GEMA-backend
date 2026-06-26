"""Caso de uso para listar el historial de cambios de estado de un activo."""

from datetime import datetime

from app.application.dtos.asset_state_log_dtos import AssetStateLogResponse
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.value_objects.identifier import AssetId, CompanyId


class ListAssetStateLogUseCase:
    """Caso de uso para listar el historial de cambios de estado de un activo."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(
        self, company_id_str: str, activo_id_str: str
    ) -> list[AssetStateLogResponse]:
        """Ejecuta la consulta del historial de estados de un activo.

        Args:
            company_id_str: Identificador de la empresa (tenant).
            activo_id_str: Identificador del activo.

        Returns:
            Lista de registros de cambio de estado ordenados cronológicamente.
        """
        company_id = CompanyId.from_string(company_id_str)
        activo_id = AssetId.from_string(activo_id_str)
        async with self.uow:
            logs = await self.uow.asset_state_logs.list_by_asset(activo_id, company_id)
            return [
                AssetStateLogResponse(
                    id=str(log.id),
                    empresa_id=str(log.empresa_id),
                    activo_id=str(log.activo_id),
                    estado_anterior=log.estado_anterior.value
                    if log.estado_anterior
                    else None,
                    estado_nuevo=log.estado_nuevo.value,
                    motivo=log.motivo,
                    fecha_cambio=(
                        log.fecha_cambio.isoformat()
                        if isinstance(log.fecha_cambio, datetime)
                        else str(log.fecha_cambio)
                    ),
                    usuario_id=str(log.usuario_id) if log.usuario_id else None,
                    version=log.version,
                )
                for log in logs
            ]
