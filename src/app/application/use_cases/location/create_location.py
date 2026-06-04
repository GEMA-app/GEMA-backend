import uuid
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.application.dtos.location_dtos import CreateLocationRequest, LocationResponse
from app.domain.entities import Location
from app.domain.value_objects import LocationId, CompanyId
from app.domain.enums import LocationType
from app.domain.exceptions import LocationNotFoundError, LocationInvalidTypeHierarchyError


class CreateLocationUseCase:
    """Caso de uso para registrar una nueva ubicación física jerárquica."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(self, company_id_str: str, request: CreateLocationRequest) -> LocationResponse:
        company_id = CompanyId.from_string(company_id_str)
        tipo = LocationType(request.tipo)

        async with self.uow:
            parent_id = None
            parent_tipo = None
            if request.parent_id:
                parent_id = LocationId.from_string(request.parent_id)
                parent_loc = await self.uow.locations.get_by_id(parent_id, company_id)
                if not parent_loc:
                    raise LocationNotFoundError(f"La ubicación padre con ID '{request.parent_id}' no existe.")
                parent_tipo = parent_loc.tipo

            # Validar jerarquía de tipos
            if tipo == LocationType.HEADQUARTERS:
                if parent_tipo is not None:
                    raise LocationInvalidTypeHierarchyError("Una sede (HEADQUARTERS) no puede tener una ubicación padre.")
            elif tipo == LocationType.PLANT:
                if parent_tipo != LocationType.HEADQUARTERS:
                    raise LocationInvalidTypeHierarchyError("Una planta (PLANT) debe tener una sede (HEADQUARTERS) como padre.")
            elif tipo == LocationType.AREA:
                if parent_tipo != LocationType.PLANT:
                    raise LocationInvalidTypeHierarchyError("Un área (AREA) debe tener una planta (PLANT) como padre.")
            elif tipo == LocationType.SECTION:
                if parent_tipo != LocationType.AREA:
                    raise LocationInvalidTypeHierarchyError("Una sección (SECTION) debe tener un área (AREA) como padre.")

            location = Location(
                id=LocationId(uuid.uuid4()),
                empresa_id=company_id,
                parent_id=parent_id,
                nombre=request.nombre.strip(),
                tipo=tipo,
                descripcion=request.descripcion
            )

            await self.uow.locations.save(location)
            await self.uow.commit()

            return LocationResponse(
                id=str(location.id),
                empresa_id=str(location.empresa_id),
                parent_id=str(location.parent_id) if location.parent_id else None,
                nombre=location.nombre,
                tipo=location.tipo.value,
                descripcion=location.descripcion
            )
