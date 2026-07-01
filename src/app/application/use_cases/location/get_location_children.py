"""Caso de uso para get location children."""

from app.application.dtos.location_dtos import LocationResponse
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.exceptions import LocationNotFoundError
from app.domain.value_objects import CompanyId, LocationId


class GetLocationChildrenUseCase:
    """Caso de uso para obtener los hijos directos de una ubicación."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(self, company_id_str: str, parent_id_str: str) -> list[LocationResponse]:
        """Obtiene los hijos directos de una ubicación."""
        company_id = CompanyId.from_string(company_id_str)
        parent_id = LocationId.from_string(parent_id_str)

        async with self.uow:
            parent = await self.uow.locations.get_by_id(parent_id, company_id)
            if not parent:
                raise LocationNotFoundError(
                    f"La ubicación padre con ID '{parent_id_str}' no existe en esta empresa."
                )

            children = await self.uow.locations.get_children(parent_id, company_id)
            return [
                LocationResponse(
                    id=str(c.id),
                    empresa_id=str(c.empresa_id),
                    parent_id=str(c.parent_id) if c.parent_id else None,
                    nombre=c.nombre,
                    tipo=c.tipo.value,
                    descripcion=c.descripcion,
                    version=c.version,
                )
                for c in children
            ]
