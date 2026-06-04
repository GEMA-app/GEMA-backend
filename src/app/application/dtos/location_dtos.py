from dataclasses import dataclass
from typing import Optional, Any


@dataclass(frozen=True)
class CreateLocationRequest:
    nombre: str
    tipo: str
    parent_id: Optional[str] = None
    descripcion: Optional[str] = None


@dataclass(frozen=True)
class UpdateLocationRequest:
    nombre: Optional[str] = None
    tipo: Optional[str] = None
    parent_id: Optional[str] = None
    descripcion: Optional[str] = None


@dataclass(frozen=True)
class LocationResponse:
    id: str
    empresa_id: str
    parent_id: Optional[str]
    nombre: str
    tipo: str
    descripcion: Optional[str]


@dataclass(frozen=True)
class LocationTreeResponse:
    id: str
    nombre: str
    tipo: str
    descripcion: Optional[str]
    children: list[Any]  # Lista de LocationTreeResponse
