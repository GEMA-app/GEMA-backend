from typing import Optional, Protocol, Any
from app.domain.entities import Asset
from app.domain.value_objects import AssetId, CompanyId


class AssetRepositoryPort(Protocol):
    """Puerto de repositorio para la persistencia y consulta de entidades Asset."""

    async def save(self, asset: Asset) -> None:
        """Guarda o actualiza un activo en el repositorio."""
        ...

    async def get_by_id(self, id: AssetId, empresa_id: CompanyId) -> Optional[Asset]:
        """Busca un activo por su identificador único dentro de una empresa."""
        ...

    async def list_by_company(
        self,
        empresa_id: CompanyId,
        offset: int,
        limit: int,
        filters: Optional[dict[str, Any]] = None
    ) -> tuple[list[Asset], int]:
        """Devuelve una lista paginada de activos con filtros y el conteo total."""
        ...

    async def delete(self, id: AssetId, empresa_id: CompanyId) -> None:
        """Elimina un activo por su identificador único dentro de una empresa."""
        ...
