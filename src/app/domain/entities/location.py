"""Entidad Location — ubicación física jerárquica con validación de tipos."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime

from app.domain.enums import LocationType
from app.domain.events import (
    DomainEvent,
    EventProducer,
    LocationCreated,
    LocationMoved,
)
from app.domain.exceptions import (
    EmptyLocationNameError,
    LocationCircularReferenceError,
    LocationInvalidTypeHierarchyError,
)
from app.domain.value_objects import CompanyId, LocationId


@dataclass
class Location(EventProducer):
    """Entidad con comportamiento (Rich Entity) que representa una ubicación física jerárquica."""

    id: LocationId
    empresa_id: CompanyId
    parent_id: LocationId | None
    nombre: str
    tipo: LocationType
    descripcion: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    _events: list[DomainEvent] = field(default_factory=list, init=False, repr=False)

    @staticmethod
    def validate_hierarchy(tipo: LocationType, parent_type: LocationType | None) -> None:
        """Valida que la jerarquía de tipos de ubicación sea correcta.

        Args:
            tipo: El tipo de ubicación a validar.
            parent_type: El tipo de la ubicación padre, o None si es raíz.

        Raises:
            LocationInvalidTypeHierarchyError: Si la combinación de tipos no es válida.
        """
        if tipo == LocationType.HEADQUARTERS and parent_type is not None:
            raise LocationInvalidTypeHierarchyError(
                "Una sede (HEADQUARTERS) no puede tener una ubicación padre."
            )
        elif tipo == LocationType.PLANT and parent_type != LocationType.HEADQUARTERS:
            raise LocationInvalidTypeHierarchyError(
                "Una planta (PLANT) debe tener una sede (HEADQUARTERS) como padre."
            )
        elif tipo == LocationType.AREA and parent_type != LocationType.PLANT:
            raise LocationInvalidTypeHierarchyError(
                "Un área (AREA) debe tener una planta (PLANT) como padre."
            )
        elif tipo == LocationType.SECTION and parent_type != LocationType.AREA:
            raise LocationInvalidTypeHierarchyError(
                "Una sección (SECTION) debe tener un área (AREA) como padre."
            )

    def pull_events(self) -> list[DomainEvent]:
        """Extrae y limpia la lista de eventos acumulados."""
        events = self._events.copy()
        self._events.clear()
        return events

    @classmethod
    def create(
        cls,
        empresa_id: CompanyId,
        parent_id: LocationId | None,
        nombre: str,
        tipo: LocationType,
        parent_type: LocationType | None,
        descripcion: str | None = None,
    ) -> "Location":
        """Crea una nueva ubicación validando la jerarquía y emitiendo LocationCreated.

        Args:
            empresa_id: Identificador de la empresa.
            parent_id: Identificador de la ubicación padre, o None si es raíz.
            nombre: Nombre de la ubicación.
            tipo: Tipo de ubicación (HEADQUARTERS, PLANT, AREA, SECTION).
            parent_type: Tipo de la ubicación padre, necesario para validar jerarquía.
            descripcion: Descripción opcional de la ubicación.
        """
        cls.validate_hierarchy(tipo, parent_type)
        location = cls(
            id=LocationId(uuid.uuid4()),
            empresa_id=empresa_id,
            parent_id=parent_id,
            nombre=nombre,
            tipo=tipo,
            descripcion=descripcion,
        )
        location._events.append(
            LocationCreated(location_id=str(location.id), empresa_id=str(empresa_id))
        )
        return location

    def move(self, new_parent_id: LocationId | None, new_parent_type: LocationType | None) -> None:
        """Cambia el padre de la ubicación y re-valida su jerarquía de tipos.

        Args:
            new_parent_id: El ID de la nueva ubicación padre, o None si pasa a ser raíz.
            new_parent_type: El tipo de la ubicación padre, o None si pasa a ser raíz.

        Raises:
            LocationCircularReferenceError: Si se intenta asignar la ubicación como su propio padre.
            LocationInvalidTypeHierarchyError: Si la combinación de tipos padre/hijo no es válida.
        """
        if new_parent_id is not None and new_parent_id == self.id:
            raise LocationCircularReferenceError("Una ubicación no puede ser padre de sí misma.")
        Location.validate_hierarchy(self.tipo, new_parent_type)
        old_parent = self.parent_id
        self.parent_id = new_parent_id
        self._events.append(
            LocationMoved(
                location_id=str(self.id),
                previous_parent_id=str(old_parent) if old_parent else None,
                new_parent_id=str(new_parent_id) if new_parent_id else None,
            )
        )

    def rename(self, new_name: str) -> None:
        """Cambia el nombre de la ubicación.

        Args:
            new_name: El nuevo nombre para la ubicación.

        Raises:
            EmptyLocationNameError: Si el nuevo nombre está vacío o solo contiene espacios.
        """
        if not new_name or not new_name.strip():
            raise EmptyLocationNameError("El nombre de la ubicación no puede estar vacío.")
        self.nombre = new_name.strip()
