from dataclasses import dataclass
from typing import Optional
from app.domain.value_objects import LocationId, CompanyId
from app.domain.enums import LocationType


@dataclass
class Location:
    """Entidad de dominio que representa una ubicación física jerárquica."""
    id: LocationId
    empresa_id: CompanyId
    parent_id: Optional[LocationId]
    nombre: str
    tipo: LocationType
    descripcion: Optional[str] = None
