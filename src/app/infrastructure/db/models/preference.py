import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base
from app.infrastructure.db.models.mixins import TenantMixin, TimestampMixin


class UserPreferenceModel(TenantMixin, TimestampMixin, Base):
    """Modelo ORM para la tabla preferencias_usuarios (1:1 con usuarios)."""

    __tablename__ = "preferencias_usuarios"

    usuario_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True
    )
    tema: Mapped[str] = mapped_column(String(20), nullable=False, default="oscuro")
