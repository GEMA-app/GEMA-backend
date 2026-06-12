from dataclasses import dataclass


@dataclass(frozen=True)
class PreferenceResponse:
    usuario_id: str
    empresa_id: str
    tema: str
    version: int = 0


@dataclass(frozen=True)
class UpdatePreferenceRequest:
    tema: str | None = None
    version: int | None = None
