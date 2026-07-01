"""Repositorio base para entidades multi-tenant con filtro por empresa_id."""

from abc import ABC

from sqlalchemy import delete, select

from app.domain.value_objects import CompanyId
from app.infrastructure.repositories.base import EntityT, IdT, ModelT, SqlAlchemyRepository


class SqlAlchemyTenantRepository(SqlAlchemyRepository[ModelT, EntityT, IdT], ABC):
    """Repositorio base para entidades multi-tenant.

    Extiende SqlAlchemyRepository con firma tenant-aware para get_by_id y delete.
    """

    async def get_by_id(self, id: IdT, empresa_id: CompanyId) -> EntityT | None:  # type: ignore[override]
        """Busca una entidad por ID filtrado por tenant.

        Returns:
            La entidad encontrada o None si no existe.
        """
        id_val = id.value if hasattr(id, "value") else id
        pk_attr = getattr(self.model_class, self.pk_column)
        stmt = select(self.model_class).where(
            pk_attr == id_val,
            self.model_class.empresa_id == empresa_id.value,  # type: ignore[attr-defined]
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_entity(model)

    async def delete(self, id: IdT, empresa_id: CompanyId) -> None:  # type: ignore[override]
        """Elimina una entidad por ID filtrado por tenant."""
        id_val = id.value if hasattr(id, "value") else id
        pk_attr = getattr(self.model_class, self.pk_column)
        stmt = delete(self.model_class).where(
            pk_attr == id_val,
            self.model_class.empresa_id == empresa_id.value,  # type: ignore[attr-defined]
        )
        await self.session.execute(stmt)
