"""Puerto para el repositorio de intervenciones técnicas."""

from typing import Protocol

from app.domain.entities.intervencion_tecnica import IntervencionTecnica
from app.domain.value_objects.identifier import IntervencionId, OrdenTrabajoId, UserId


class IntervencionRepositoryPort(Protocol):
    """Contrato para el repositorio de intervenciones técnicas."""

    async def save(self, intervencion: IntervencionTecnica) -> None:
        """Persiste una intervención técnica en la base de datos."""
        ...

    async def get_by_id(
        self, id: IntervencionId, empresa_id: CompanyId
    ) -> IntervencionTecnica | None:
        """Obtiene una intervención por su ID y empresa."""
        ...

    async def get_by_orden_trabajo(
        self, orden_trabajo_id: OrdenTrabajoId, empresa_id: CompanyId
    ) -> list[IntervencionTecnica]:
        """Obtiene todas las intervenciones de una orden de trabajo."""
        ...

    async def get_by_tecnico(
        self, tecnico_id: UserId, empresa_id: CompanyId
    ) -> list[IntervencionTecnica]:
        """Obtiene todas las intervenciones realizadas por un técnico."""
        ...

    async def list(
        self, empresa_id: CompanyId, offset: int = 0, limit: int = 100
    ) -> tuple[list[IntervencionTecnica], int]:
        """Lista todas las intervenciones de una empresa con paginación."""
        ...