from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional

class ReporteFalla:
    def __init__(
        self,
        titulo: str,
        descripcion: str,
        ubicacion: str,
        prioridad: str,
        reportado_por: str,
        id: Optional[UUID] = None,
        estado: str = "ABIERTO",
        fecha_creacion: Optional[datetime] = None
    ):
        self.id = id or uuid4()
        self.titulo = titulo
        self.descripcion = descripcion
        self.ubicacion = ubicacion
        self.prioridad = prioridad
        self.reportado_por = reportado_por
        self.estado = estado
        self.fecha_creacion = fecha_creacion or datetime.utcnow()