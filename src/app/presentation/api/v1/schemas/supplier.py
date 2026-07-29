"""Schemas de solicitud y respuesta JSON:API para Proveedores."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class SupplierAttributes(BaseModel):
    """Atributos de un proveedor según JSON:API.

    Attributes:
        empresa_id: UUID de la empresa a la que pertenece.
        name: Nombre del proveedor.
        rif: RIF del proveedor.
        phone: Teléfono de contacto.
        email: Correo electrónico.
        contact: Persona de contacto.
        version: Versión para control de concurrencia optimista.
    """

    empresa_id: str
    name: str
    rif: str | None
    phone: str | None
    email: str | None
    contact: str | None
    activo: bool = True
    direccion: str | None = None
    version: int
    created_at: datetime | None = None
    updated_at: datetime | None = None


class SupplierResource(BaseModel):
    """Recurso JSON:API que envuelve los atributos del proveedor."""

    type: str = Field(default="suppliers")
    id: str
    attributes: SupplierAttributes


class SupplierDocument(BaseModel):
    """Documento JSON:API con un único recurso de proveedor."""

    data: SupplierResource
    meta: dict[str, Any] | None = None


class SupplierListDocument(BaseModel):
    """Documento JSON:API con una lista de recursos de proveedor."""

    data: list[SupplierResource]
    meta: dict[str, Any] | None = None


_RIF_PATTERN_STR = r"^[JGVEPjgivep]-\d{8}-\d$"


class CreateSupplierAttributes(BaseModel):
    """Atributos para crear un proveedor."""

    name: str = Field(..., min_length=1, max_length=150)
    rif: str | None = Field(None, max_length=20, pattern=_RIF_PATTERN_STR)
    phone: str | None = Field(None, max_length=30)
    email: str | None = Field(None, max_length=100)
    contact: str | None = Field(None, max_length=100)
    direccion: str | None = Field(None, max_length=255)


class CreateSupplierResource(BaseModel):
    """Recurso JSON:API para crear un proveedor."""

    type: str = Field(default="suppliers", description="Tipo de recurso")
    attributes: CreateSupplierAttributes


class CreateSupplierRequest(BaseModel):
    """Solicitud JSON:API para crear un proveedor."""

    data: CreateSupplierResource


class UpdateSupplierAttributes(BaseModel):
    """Atributos para actualizar un proveedor."""

    name: str | None = Field(None, min_length=1, max_length=150)
    rif: str | None = Field(None, max_length=20, pattern=_RIF_PATTERN_STR)
    phone: str | None = Field(None, max_length=30)
    email: str | None = Field(None, max_length=100)
    contact: str | None = Field(None, max_length=100)
    activo: bool | None = Field(None)
    direccion: str | None = Field(None, max_length=255)
    version: int | None = Field(None, description="Versión para locking optimista")


class UpdateSupplierResource(BaseModel):
    """Recurso JSON:API para actualizar un proveedor."""

    type: str = Field(default="suppliers", description="Tipo de recurso")
    attributes: UpdateSupplierAttributes


class UpdateSupplierRequest(BaseModel):
    """Solicitud JSON:API para actualizar un proveedor."""

    data: UpdateSupplierResource
