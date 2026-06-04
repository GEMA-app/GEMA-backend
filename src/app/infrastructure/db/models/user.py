import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base
from app.infrastructure.db.models.mixins import TenantMixin, TimestampMixin

if TYPE_CHECKING:
    from app.infrastructure.db.models.role import RoleModel


class UserModel(TenantMixin, TimestampMixin, Base):
    """Modelo ORM de SQLAlchemy para la tabla de usuarios."""

    __tablename__ = "usuarios"
    __table_args__ = (UniqueConstraint("empresa_id", "email", name="uq_usuarios_empresa_email"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    telefono: Mapped[str] = mapped_column(String(50), nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relación con roles a través de la tabla asociativa roles_usuarios
    roles: Mapped[list["RoleModel"]] = relationship(
        "RoleModel", secondary="roles_usuarios", back_populates="usuarios", lazy="selectin"
    )
