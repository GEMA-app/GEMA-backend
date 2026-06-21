from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from uuid import UUID

class AssetStateLogResponse(BaseModel):
    id: int
    activo_id: UUID
    estado_anterior: Optional[str] = None
    estado_nuevo: str
    fecha_cambio: datetime
    usuario_id: Optional[UUID] = None

    # Configuración oficial de Pydantic v2 para leer los modelos de SQLAlchemy
    model_config = ConfigDict(from_attributes=True)