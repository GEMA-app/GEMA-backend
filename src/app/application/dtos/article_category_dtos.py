from pydantic import BaseModel, Field
from uuid import UUID

class CreateCategoryRequest(BaseModel):
    model_config = {"frozen": True}
    nombre: str = Field(..., min_length=1, max_length=100)
    descripcion: str | None = Field(None, max_length=255)

class UpdateCategoryRequest(BaseModel):
    model_config = {"frozen": True}
    nombre: str | None = Field(None, min_length=1, max_length=100)
    descripcion: str | None = Field(None, max_length=255)

class ArticleCategoryResponse(BaseModel):
    model_config = {"frozen": True}
    id: UUID
    empresa_id: UUID
    nombre: str
    descripcion: str | None
    version: int