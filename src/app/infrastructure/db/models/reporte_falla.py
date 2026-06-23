from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from app.infrastructure.db.base import Base
from datetime import datetime
import uuid

class ReporteFallaModel(Base):
    __tablename__ = "reportes_fallas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    titulo = Column(String(100), nullable=False)
    descripcion = Column(String, nullable=False)
    ubicacion = Column(String, nullable=False)
    prioridad = Column(String, default="MEDIA", nullable=False)
    reportado_por = Column(String, nullable=False)
    estado = Column(String, default="ABIERTO", nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)