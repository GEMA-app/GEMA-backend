import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, declared_attr, mapped_column


class TenantMixin:
    """Mixin que agrega empresa_id con FK e índice a cualquier modelo multi-tenant."""

    empresa_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True
    )


class TimestampMixin:
    """Mixin que agrega created_at y updated_at con timezone awareness."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )


class VersionMixin:
    """Mixin para optimistic locking con columna de versión."""

    version: Mapped[int] = mapped_column(default=1, nullable=False)

    @declared_attr  # type: ignore[arg-type]
    def __mapper_args__(cls) -> dict[str, Any]:
        return {"version_id_col": cls.version}
