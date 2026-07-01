"""Caso de uso para update location."""

from app.application.dtos.location_dtos import LocationResponse, UpdateLocationRequest
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.entities import Location
from app.domain.enums import LocationType
from app.domain.exceptions import (
    LocationCircularReferenceError,
    LocationNotFoundError,
    StaleDataError,
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

            if request.version is not None and request.version != location.version:
                raise StaleDataError(
                    f"Conflicto de versión para ubicación: se esperaba {request.version}, "
                    f"la actual es {location.version}."
                )

            new_parent_id = location.parent_id

            if "parent_id" in request._fields_set:
                if request.parent_id is not None:
                    p_id_str = request.parent_id.strip()
                    if not p_id_str:
                        raise ValidationException("El parent_id no puede estar vacío.")
                    p_id = LocationId.from_string(p_id_str)
                    if p_id == location.id:
                        raise LocationCircularReferenceError(
                            "Una ubicación no puede ser su propio padre."
                        )

                    curr_id: LocationId | None = p_id
                    visited_set = {location.id}
                    while curr_id is not None:
                        if curr_id in visited_set:
                            raise LocationCircularReferenceError(
                                "Referencia circular detectada en la jerarquía de ubicaciones."
                            )
                        visited_set.add(curr_id)
                        curr_loc = await self.uow.locations.get_by_id(curr_id, company_id)
                        if not curr_loc:
                            break
                        curr_id = curr_loc.parent_id

                    parent_loc = await self.uow.locations.get_by_id(p_id, company_id)
                    if not parent_loc:
                        raise LocationNotFoundError(
                            f"La ubicación padre con ID '{p_id_str}' no existe."
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

            if "nombre" in request._fields_set:
                if request.nombre is None or not request.nombre.strip():
                    raise ValidationException("El nombre de la ubicación no puede estar vacío.")
                location.nombre = request.nombre.strip()

            if "descripcion" in request._fields_set:
                location.descripcion = request.descripcion

            if "tipo" in request._fields_set or "parent_id" in request._fields_set:
                if "tipo" in request._fields_set and request.tipo is None:
                    raise ValidationException("El tipo de ubicación no puede ser nulo.")
                new_tipo_enum = (
                    LocationType(request.tipo)
                    if ("tipo" in request._fields_set and request.tipo is not None)
                    else None
                )

                # P3h: Validar descendientes al cambiar tipo
                old_tipo = location.tipo
                new_tipo = new_tipo_enum if new_tipo_enum is not None else old_tipo
                if new_tipo != old_tipo:
                    from app.domain.exceptions import LocationInvalidTypeHierarchyError

                    children = await self.uow.locations.get_children(location.id, company_id)
                    for child in children:
                        try:
                            Location.validate_hierarchy(child.tipo, new_tipo)
                        except LocationInvalidTypeHierarchyError as err:
                            raise ValidationException(
                                f"El cambio a {new_tipo.value} invalida la ubicación hija "
                                f"'{child.nombre}' (tipo: {child.tipo.value})."
                            ) from err

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
                version=location.version,
            )
