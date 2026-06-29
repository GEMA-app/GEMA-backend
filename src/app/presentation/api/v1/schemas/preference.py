"""Schemas JSON:API para preferencias de usuario: atributos,
recursos, documentos y solicitudes de actualización.
"""

from typing import Any

from pydantic import BaseModel, Field


class PreferenceAttributes(BaseModel):
    """Atributos de las preferencias de usuario."""

    empresa_id: str
    tema: str
    version: int


class PreferenceResource(BaseModel):
    """Recurso JSON:API de preferencias de usuario."""

    type: str = Field(default="preferences")
    id: str
    attributes: PreferenceAttributes


class PreferenceDocument(BaseModel):
    """Documento JSON:API con preferencias de usuario."""

    data: PreferenceResource
    meta: dict[str, Any] | None = None


# Solicitud de actualización
class UpdatePreferenceAttributes(BaseModel):
    """Atributos para actualizar preferencias."""

    tema: str | None = None
    version: int | None = None


class UpdatePreferenceResource(BaseModel):
    """Recurso JSON:API para actualizar preferencias."""

    type: str = Field(default="preferences")
    id: str
    attributes: UpdatePreferenceAttributes


class UpdatePreferenceRequest(BaseModel):
    """Solicitud JSON:API para actualizar preferencias."""

    data: UpdatePreferenceResource
