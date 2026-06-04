from app.application.dtos.location_dtos import LocationResponse, UpdateLocationRequest
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.enums import LocationType
from app.domain.exceptions import (
    LocationCircularReferenceError,
    LocationInvalidTypeHierarchyError,
    LocationNotFoundError,
)
from app.domain.value_objects import CompanyId, LocationId


class UpdateLocationUseCase:
    """Caso de uso para actualizar una ubicación física jerárquica con validación de ciclos y tipos."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(
        self, company_id_str: str, location_id_str: str, request: UpdateLocationRequest
    ) -> LocationResponse:
        company_id = CompanyId.from_string(company_id_str)
        location_id = LocationId.from_string(location_id_str)

        async with self.uow:
            location = await self.uow.locations.get_by_id(location_id, company_id)
            if not location:
                raise LocationNotFoundError(
                    f"La ubicación con ID '{location_id_str}' no existe en esta empresa."
                )

            new_parent_id = location.parent_id
            new_tipo = location.tipo

            if request.tipo is not None:
                new_tipo = LocationType(request.tipo)

            if request.parent_id is not None:
                if request.parent_id:
                    p_id = LocationId.from_string(request.parent_id)
                    if p_id == location.id:
                        raise LocationCircularReferenceError(
                            "Una ubicación no puede ser su propio padre."
                        )

                    curr_id: LocationId | None = p_id
                    while curr_id is not None:
                        curr_loc = await self.uow.locations.get_by_id(curr_id, company_id)
                        if not curr_loc:
                            break
                        if curr_loc.id == location.id:
                            raise LocationCircularReferenceError(
                                "Referencia circular detectada en la jerarquía de ubicaciones."
                            )
                        curr_id = curr_loc.parent_id

                    parent_loc = await self.uow.locations.get_by_id(p_id, company_id)
                    if not parent_loc:
                        raise LocationNotFoundError(
                            f"La ubicación padre con ID '{request.parent_id}' no existe."
                        )
                    new_parent_id = p_id
                    parent_tipo = parent_loc.tipo
                else:
                    new_parent_id = None
                    parent_tipo = None
            else:
                if location.parent_id:
                    parent_loc = await self.uow.locations.get_by_id(location.parent_id, company_id)
                    parent_tipo = parent_loc.tipo if parent_loc else None
                else:
                    parent_tipo = None

            # Validar jerarquía de tipos
            if new_tipo == LocationType.HEADQUARTERS:
                if parent_tipo is not None:
                    raise LocationInvalidTypeHierarchyError(
                        "Una sede (HEADQUARTERS) no puede tener una ubicación padre."
                    )
            elif new_tipo == LocationType.PLANT:
                if parent_tipo != LocationType.HEADQUARTERS:
                    raise LocationInvalidTypeHierarchyError(
                        "Una planta (PLANT) debe tener una sede (HEADQUARTERS) como padre."
                    )
            elif new_tipo == LocationType.AREA:
                if parent_tipo != LocationType.PLANT:
                    raise LocationInvalidTypeHierarchyError(
                        "Un área (AREA) debe tener una planta (PLANT) como padre."
                    )
            elif new_tipo == LocationType.SECTION:
                if parent_tipo != LocationType.AREA:
                    raise LocationInvalidTypeHierarchyError(
                        "Una sección (SECTION) debe tener un área (AREA) como padre."
                    )

            if request.nombre is not None:
                if not request.nombre.strip():
                    raise ValueError("El nombre de la ubicación no puede estar vacío.")
                location.nombre = request.nombre.strip()

            if request.descripcion is not None:
                location.descripcion = request.descripcion

            location.tipo = new_tipo
            location.parent_id = new_parent_id

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
