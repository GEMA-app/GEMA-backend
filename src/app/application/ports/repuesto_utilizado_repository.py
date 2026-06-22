from typing import Protocol
from uuid import UUID

from app.domain.entities.repuesto_utilizado import RepuestoUtilizado
from app.domain.value_objects import CompanyId, InterventionId


class RepuestoUtilizadoRepositoryPort(Protocol):
    """Puerto para el repositorio de repuestos utilizados."""

    async def get_by_id(self, id: UUID) -> RepuestoUtilizado | None:
        """Obtiene un repuesto utilizado por su ID."""
        ...

    async def get_by_intervention(
        self, company_id: CompanyId, intervention_id: InterventionId
    ) -> list[RepuestoUtilizado]:
        """Lista todos los repuestos utilizados en una intervención."""
        ...

    async def save(self, repuesto_utilizado: RepuestoUtilizado) -> None:
        """Guarda un repuesto utilizado (INSERT o UPDATE)."""
        ...

    async def delete(self, id: UUID) -> None:
        """Elimina un repuesto utilizado por su ID."""
        ...