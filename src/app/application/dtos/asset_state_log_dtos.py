"""DTOs para el módulo AssetStateLog (historial de cambios de estado de activos)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class AssetStateLogResponse:
    """DTO de salida con los datos de un registro de cambio de estado."""

    id: str
    empresa_id: str
    activo_id: str
    estado_anterior: str | None
    estado_nuevo: str
    motivo: str | None
    fecha_cambio: str
    usuario_id: str | None
    version: int
