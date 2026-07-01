"""Modelos ORM de SQLAlchemy para roles, permisos y asignaciones."""

import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums import PermissionModule
from app.infrastructure.db.base import Base
from app.infrastructure.db.models.mixins import TenantMixin, TimestampMixin, VersionMixin

if TYPE_CHECKING:
    from app.infrastructure.db.models.user import UserModel


class RoleUserModel(Base):
    """Modelo ORM para la tabla asociativa de roles y usuarios."""

    __tablename__ = "roles_usuarios"

    usuario_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True
    )
    rol_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )


class PermissionModel(TenantMixin, TimestampMixin, Base):
    """Modelo ORM para la tabla de permisos asignados a roles."""

    __tablename__ = "permisos"
    __table_args__ = (
        UniqueConstraint("empresa_id", "rol_id", "modulo", name="uq_permisos_empresa_rol_modulo"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    rol_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("roles.id", ondelete="CASCADE"), nullable=False
    )
    modulo: Mapped[PermissionModule] = mapped_column(
        Enum(
            PermissionModule,
            name="modulo_permiso",
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
    )
    puede_ver: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    puede_crear: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    puede_editar: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    puede_eliminar: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    rol: Mapped["RoleModel"] = relationship("RoleModel", back_populates="permisos")


class RoleModel(VersionMixin, TenantMixin, TimestampMixin, Base):
    """Modelo ORM para la tabla de roles."""

    __tablename__ = "roles"
    __table_args__ = (UniqueConstraint("empresa_id", "nombre", name="uq_roles_empresa_nombre"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)

    permisos: Mapped[list[PermissionModel]] = relationship(
        "PermissionModel", back_populates="rol", cascade="all, delete-orphan", lazy="selectin"
    )

    usuarios: Mapped[list["UserModel"]] = relationship(
        "UserModel", secondary="roles_usuarios", back_populates="roles", lazy="selectin"
    )
