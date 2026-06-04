from dataclasses import dataclass

from app.domain.enums import LocationType
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
