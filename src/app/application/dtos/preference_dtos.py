"""DTOs de entrada y salida para el módulo de Preference."""

from dataclasses import dataclass


@dataclass(frozen=True)
class PreferenceResponse:
    """DTO de salida con las preferencias del usuario."""

    usuario_id: str
    empresa_id: str
    tema: str
    version: int = 0


@dataclass(frozen=True)
class UpdatePreferenceRequest:
    """DTO de entrada para la actualización de preferencias de usuario."""

    tema: str | None = None
    version: int | None = None
