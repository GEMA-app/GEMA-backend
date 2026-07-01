"""Puerto (Protocol) del repositorio de Preference."""
from typing import Protocol

from app.domain.entities import UserPreference
from app.domain.value_objects import CompanyId, UserId


class PreferenceRepositoryPort(Protocol):
    """Puerto de repositorio para preferencias de usuario."""

    async def get_by_user(
        self, usuario_id: UserId, empresa_id: CompanyId
    ) -> UserPreference | None:
        """Obtiene las preferencias de un usuario en una empresa."""
        ...

    async def save(self, preference: UserPreference) -> None:
        """Persiste la entidad (INSERT si no existe, UPDATE si existe)."""
        ...
