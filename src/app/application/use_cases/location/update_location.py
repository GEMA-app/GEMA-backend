from app.application.dtos.location_dtos import LocationResponse, UpdateLocationRequest
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.entities import Location
from app.domain.enums import LocationType
from app.domain.exceptions import (
    LocationCircularReferenceError,
    LocationNotFoundError,
    ValidationException,
)
from app.domain.value_objects import CompanyId, LocationId


class UpdateLocationUseCase:
    """Actualiza los datos de una ubicación jerárquica."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        """Guarda dependencias."""
        self.uow = uow

    async def execute(
        self, company_id_str: str, location_id_str: str, request: UpdateLocationRequest
    ) -> LocationResponse:
        """Actualiza los datos de la ubicación."""
        company_id = CompanyId.from_string(company_id_str)
        location_id = LocationId.from_string(location_id_str)

        async with self.uow:
            location = await self.uow.locations.get_by_id(location_id, company_id)
            if not location:
                raise LocationNotFoundError(
                    f"La ubicación con ID '{location_id_str}' no existe en esta empresa."
                )

            new_parent_id = location.parent_id

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
                    parent_type = parent_loc.tipo
                else:
                    new_parent_id = None
                    parent_type = None
            else:
                if location.parent_id:
                    parent_loc = await self.uow.locations.get_by_id(location.parent_id, company_id)
                    parent_type = parent_loc.tipo if parent_loc else None
                else:
                    parent_type = None

            if request.nombre is not None:
                if not request.nombre.strip():
                    raise ValidationException("El nombre de la ubicación no puede estar vacío.")
                location.nombre = request.nombre.strip()

            if request.descripcion is not None:
                location.descripcion = request.descripcion

            # Delegar cambio de parent y/o tipo al método de dominio move()
            # que valida jerarquía, detecta auto-referencia y emite LocationMoved
            if request.tipo is not None or request.parent_id is not None:
                new_tipo_enum = LocationType(request.tipo) if request.tipo is not None else None
                location.move(new_parent_id, parent_type, new_tipo=new_tipo_enum)

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
