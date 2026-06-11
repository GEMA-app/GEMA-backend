

from app.application.dtos.location_dtos import CreateLocationRequest, LocationResponse
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.entities import Location
from app.domain.enums import LocationType
from app.domain.exceptions import LocationNotFoundError
from app.domain.value_objects import CompanyId, LocationId


class CreateLocationUseCase:
    """Registra una ubicación jerárquica en la empresa."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        """Guarda dependencias."""
        self.uow = uow

    async def execute(
        self, company_id_str: str, request: CreateLocationRequest
    ) -> LocationResponse:
        """Crea una nueva ubicación física."""
        company_id = CompanyId.from_string(company_id_str)
        tipo = LocationType(request.tipo)

        async with self.uow:
            parent_id = None
            parent_type = None
            if request.parent_id:
                parent_id = LocationId.from_string(request.parent_id)
                parent_loc = await self.uow.locations.get_by_id(parent_id, company_id)
                if not parent_loc:
                    raise LocationNotFoundError(
                        f"La ubicación padre con ID '{request.parent_id}' no existe."
                    )
                parent_type = parent_loc.tipo

            location = Location.create(
                empresa_id=company_id,
                parent_id=parent_id,
                nombre=request.nombre.strip(),
                tipo=tipo,
                parent_type=parent_type,
                descripcion=request.descripcion,
            )

            await self.uow.locations.save(location)
            await self.uow.commit()

            return LocationResponse(
                id=str(location.id),
                empresa_id=str(location.empresa_id),
                parent_id=str(location.parent_id) if location.parent_id else None,
                nombre=location.nombre,
                tipo=location.tipo.value,
                descripcion=location.descripcion,
            )
