"""Entidad AssetStateLog — registro auditable de cambio de estado de un activo."""

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from app.domain.enums import AssetStatus
from app.domain.value_objects.identifier import AssetId, CompanyId


@dataclass
class AssetStateLog:
    """Entidad que representa un cambio de estado en el historial del activo.

    Registra la transición de estado_anterior a estado_nuevo, la fecha
    del cambio y el usuario responsable.
    """

    id: uuid.UUID
    empresa_id: CompanyId
    activo_id: AssetId
    estado_anterior: AssetStatus | None
    estado_nuevo: AssetStatus
    motivo: str | None
    fecha_cambio: datetime | None = None
    usuario_id: uuid.UUID | None = None
    version: int = 1

    @classmethod
    def create(
        cls,
        empresa_id: CompanyId,
        activo_id: AssetId,
        estado_nuevo: AssetStatus,
        motivo: str | None = None,
        estado_anterior: AssetStatus | None = None,
        usuario_id: uuid.UUID | None = None,
    ) -> "AssetStateLog":
        """Crea un registro auditable de cambio de estado.

        Args:
            empresa_id: Identificador del tenant.
            activo_id: Identificador del activo.
            estado_nuevo: Estado al que transiciona el activo.
            motivo: Razón del cambio.
            estado_anterior: Estado previo del activo (opcional).
            usuario_id: Usuario que ejecutó el cambio (opcional).

        Returns:
            Nueva instancia de AssetStateLog.
        """
        return cls(
            id=uuid.uuid4(),
            empresa_id=empresa_id,
            activo_id=activo_id,
            estado_anterior=estado_anterior,
            estado_nuevo=estado_nuevo,
            motivo=motivo,
            fecha_cambio=datetime.now(UTC),
            usuario_id=usuario_id,
        )
