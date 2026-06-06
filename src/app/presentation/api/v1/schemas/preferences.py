from typing import Any

from pydantic import BaseModel, Field


class PreferenceAttributes(BaseModel):
    empresa_id: str
    tema: str


class PreferenceResource(BaseModel):
    type: str = Field(default="preferences")
    id: str
    attributes: PreferenceAttributes


class PreferenceDocument(BaseModel):
    data: PreferenceResource
    meta: dict[str, Any] | None = None


# Solicitud de actualización
class UpdatePreferenceAttributes(BaseModel):
    tema: str | None = None


class UpdatePreferenceResource(BaseModel):
    type: str = Field(default="preferences")
    id: str
    attributes: UpdatePreferenceAttributes


class UpdatePreferenceRequest(BaseModel):
    data: UpdatePreferenceResource
