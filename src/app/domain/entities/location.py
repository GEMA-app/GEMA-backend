from dataclasses import dataclass
from datetime import datetime

from app.domain.enums import LocationType
from app.domain.exceptions.location import LocationInvalidTypeHierarchyError
from app.domain.value_objects import CompanyId, LocationId


@dataclass
class Location:
    """Entidad de dominio que representa una ubicación física jerárquica."""

    id: LocationId
    empresa_id: CompanyId
    parent_id: LocationId | None
    nombre: str
    tipo: LocationType
    descripcion: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @staticmethod
    def validate_hierarchy(tipo: LocationType, parent_tipo: LocationType | None) -> None:
        """Valida que la jerarquía de tipos de ubicación sea correcta."""
        if tipo == LocationType.HEADQUARTERS and parent_tipo is not None:
            raise LocationInvalidTypeHierarchyError(
                "Una sede (HEADQUARTERS) no puede tener una ubicación padre."
            )
        elif tipo == LocationType.PLANT and parent_tipo != LocationType.HEADQUARTERS:
            raise LocationInvalidTypeHierarchyError(
                "Una planta (PLANT) debe tener una sede (HEADQUARTERS) como padre."
            )
        elif tipo == LocationType.AREA and parent_tipo != LocationType.PLANT:
            raise LocationInvalidTypeHierarchyError(
                "Un área (AREA) debe tener una planta (PLANT) como padre."
            )
        elif tipo == LocationType.SECTION and parent_tipo != LocationType.AREA:
            raise LocationInvalidTypeHierarchyError(
                "Una sección (SECTION) debe tener un área (AREA) como padre."
            )

