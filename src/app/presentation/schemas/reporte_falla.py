from pydantic import BaseModel, Field
from typing import Optional

class ReporteFallaCreate(BaseModel):
    titulo: str = Field(..., max_length=100, description="Título corto de la falla")
    descripcion: str = Field(..., description="Detalle de lo que está ocurriendo")
    ubicacion: str = Field(..., description="Lugar, área o componente afectado")
    prioridad: str = Field("MEDIA", description="BAJA, MEDIA o ALTA")
    reportado_por: str = Field(..., description="ID o nombre de quien detecta la falla")