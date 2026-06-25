from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.infrastructure.db.base import Base
from app.infrastructure.db.models.mixins import TenantMixin, TimestampMixin, VersionMixin

class ArticleCategoryModel(Base, TenantMixin, TimestampMixin, VersionMixin):
    __tablename__ = "categorias_articulos"

    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)