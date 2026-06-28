"""Puerto de repositorio para la persistencia y consulta de AssetStateLog."""

from typing import Protocol

from app.domain.entities.asset_state_log import AssetStateLog
from app.domain.value_objects.identifier import AssetId, CompanyId


class AssetStateLogRepositoryPort(Protocol):
    """Puerto de repositorio para la persistencia y consulta de AssetStateLog."""

    async def list_by_asset(
        self, activo_id: AssetId, empresa_id: CompanyId
    ) -> list[AssetStateLog]:
        """Lista los cambios de estado de un activo ordenados cronológicamente.

        Args:
            activo_id: Identificador del activo.
            empresa_id: Identificador de la empresa (tenant).

        Returns:
            Lista de registros de cambio de estado ordenados del más reciente al más antiguo.
        """
        ...

    async def save(self, entity: AssetStateLog) -> None:
        """Persiste un nuevo registro de cambio de estado.

        Args:
            entity: Entidad AssetStateLog a guardar.
        """
        ...
