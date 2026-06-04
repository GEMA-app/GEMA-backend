from app.application.ports.unit_of_work import UnitOfWorkPort
from app.application.dtos.location_dtos import LocationResponse
from app.domain.value_objects import LocationId, CompanyId
from app.domain.exceptions import LocationNotFoundError


class GetLocationUseCase:
    """Caso de uso para obtener una ubicación por su ID."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(self, company_id_str: str, location_id_str: str) -> LocationResponse:
        company_id = CompanyId.from_string(company_id_str)
        location_id = LocationId.from_string(location_id_str)

        async with self.uow:
            location = await self.uow.locations.get_by_id(location_id, company_id)
            if not location:
                raise LocationNotFoundError(f"La ubicación con ID '{location_id_str}' no existe en esta empresa.")

            return LocationResponse(
                id=str(location.id),
                empresa_id=str(location.empresa_id),
                parent_id=str(location.parent_id) if location.parent_id else None,
                nombre=location.nombre,
                tipo=location.tipo.value,
                descripcion=location.descripcion
            )
