"""Puerto (Protocol) del repositorio de Location."""

from typing import Protocol

from app.domain.entities import Location
from app.domain.value_objects import CompanyId, LocationId


class LocationRepositoryPort(Protocol):
    """Puerto de repositorio para la persistencia, consulta y gestión de ubicaciones jerárquicas."""

    async def save(self, location: Location) -> None:
        """Guarda o actualiza una ubicación en el repositorio."""
        ...

    async def get_by_id(self, id: LocationId, empresa_id: CompanyId) -> Location | None:
        """Busca una ubicación por su identificador único dentro de una empresa."""
        ...

    async def get_tree(self, empresa_id: CompanyId) -> list[Location]:
        """Obtiene el árbol jerárquico completo de ubicaciones para una empresa."""
        ...

    async def get_children(self, parent_id: LocationId, empresa_id: CompanyId) -> list[Location]:
        """Obtiene las ubicaciones hijas directas de una ubicación específica."""
        ...

    async def delete(self, id: LocationId, empresa_id: CompanyId) -> None:
        """Elimina una ubicación por su identificador único dentro de una empresa."""
        ...
