"""Puerto del repositorio de UsedPart (repuestos utilizados)."""

from typing import Protocol
from uuid import UUID

from app.domain.entities.used_part import UsedPart
from app.domain.value_objects import CompanyId, InterventionId


class UsedPartRepositoryPort(Protocol):
    """Puerto para el repositorio de repuestos utilizados."""

    async def get_by_id(self, id: UUID, empresa_id: CompanyId) -> UsedPart | None:
        """Obtiene un repuesto utilizado por su ID."""
        ...

    async def get_by_intervention(
        self, company_id: CompanyId, intervention_id: InterventionId
    ) -> list[UsedPart]:
        """Lista todos los repuestos utilizados en una intervención."""
        ...

    async def save(self, used_part: UsedPart) -> None:
        """Guarda un repuesto utilizado (INSERT o UPDATE)."""
        ...

    async def delete(self, id: UUID, empresa_id: CompanyId) -> None:
        """Elimina un repuesto utilizado por su ID."""
        ...
