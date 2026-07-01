"""Adaptador SQLAlchemy para el repositorio de proveedores."""

from uuid import UUID

from sqlalchemy import delete as sa_delete
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.supplier_repository import SupplierRepositoryPort
from app.domain.entities.supplier import Supplier
from app.domain.events import DomainEvent
from app.infrastructure.db.models.supplier import SupplierModel
from app.infrastructure.repositories.base import SqlAlchemyRepository


class SqlAlchemySupplierRepository(
    SqlAlchemyRepository[SupplierModel, Supplier, UUID],
    SupplierRepositoryPort,
):
    """Implementación concreta de SupplierRepositoryPort usando SQLAlchemy 2.0."""

    def __init__(
        self,
        session: AsyncSession,
        pending_events: list[DomainEvent] | None = None,
    ) -> None:
        super().__init__(session, SupplierModel, pending_events)

    def _to_model(self, entity: Supplier) -> SupplierModel:
        return SupplierModel(
            id=entity.id,
            empresa_id=entity.empresa_id,
            nombre=entity.name,
            rif=entity.rif,
            telefono=entity.phone,
            email=entity.email,
            contacto=entity.contact,
            version=entity.version,
        )

    def _to_entity(self, model: SupplierModel) -> Supplier:
        return Supplier(
            id=model.id,
            empresa_id=model.empresa_id,
            name=model.nombre,
            rif=model.rif,
            phone=model.telefono,
            email=model.email,
            contact=model.contacto,
            version=model.version,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def get_by_id(self, id: UUID, empresa_id: UUID) -> Supplier | None:  # type: ignore[override]
        """Busca un proveedor por ID dentro del tenant."""
        stmt = select(SupplierModel).where(
            SupplierModel.id == id,
            SupplierModel.empresa_id == empresa_id,
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def delete(self, id: UUID, empresa_id: UUID) -> None:  # type: ignore[override]
        """Elimina un proveedor por ID dentro del tenant."""
        stmt = sa_delete(SupplierModel).where(
            SupplierModel.id == id,
            SupplierModel.empresa_id == empresa_id,
        )
        await self.session.execute(stmt)

    async def get_by_rif(self, rif: str, empresa_id: UUID) -> Supplier | None:
        """Busca un proveedor por RIF exacto dentro del tenant."""
        stmt = select(SupplierModel).where(
            SupplierModel.rif == rif,
            SupplierModel.empresa_id == empresa_id,
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_all_by_company(
        self, empresa_id: UUID, search: str | None = None,
    ) -> list[Supplier]:
        """Retorna todos los proveedores de un tenant, con filtro opcional."""
        stmt = select(SupplierModel).where(SupplierModel.empresa_id == empresa_id)
        if search:
            pattern = f"%{search}%"
            stmt = stmt.where(
                SupplierModel.nombre.ilike(pattern)
                | SupplierModel.rif.ilike(pattern)
            )
        stmt = stmt.order_by(SupplierModel.nombre)
        result = await self.session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def has_inventory_parts(self, supplier_id: UUID, empresa_id: UUID) -> bool:
        """Verifica si un proveedor tiene repuestos de inventario asociados."""
        from app.infrastructure.db.models.inventory_part import InventoryPartModel

        stmt = select(InventoryPartModel.id).where(
            InventoryPartModel.proveedor_id == supplier_id,
            InventoryPartModel.empresa_id == empresa_id,
        ).limit(1)
        result = await self.session.execute(stmt)
        return result.first() is not None
