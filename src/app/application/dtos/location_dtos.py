from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CreateLocationRequest:
    nombre: str
    tipo: str
    parent_id: str | None = None
    descripcion: str | None = None


@dataclass(frozen=True)
class UpdateLocationRequest:
    nombre: str | None = None
    tipo: str | None = None
    parent_id: str | None = None
    descripcion: str | None = None


@dataclass(frozen=True)
class LocationResponse:
    id: str
    empresa_id: str
    parent_id: str | None
    nombre: str
    tipo: str
    descripcion: str | None


@dataclass(frozen=True)
class LocationTreeResponse:
    id: str
    nombre: str
    tipo: str
    descripcion: str | None
    children: list[LocationTreeResponse]
