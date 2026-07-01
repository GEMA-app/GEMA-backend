"""Puerto (Protocol) del repositorio de proveedores."""

from typing import Protocol
from uuid import UUID

from app.domain.entities.supplier import Supplier


class SupplierRepositoryPort(Protocol):
    """Contrato estructural para el repositorio de proveedores."""

    async def get_by_id(self, id: UUID, empresa_id: UUID) -> Supplier | None:
        """Busca un proveedor por ID dentro del tenant."""
        ...

    async def get_by_rif(self, rif: str, empresa_id: UUID) -> Supplier | None:
        """Busca un proveedor por RIF exacto dentro del tenant."""
        ...

    async def get_all_by_company(
        self,
        empresa_id: UUID,
        search: str | None = None,
    ) -> list[Supplier]:
        """Retorna todos los proveedores de un tenant, filtro opcional por nombre o RIF."""
        ...

    async def save(self, supplier: Supplier) -> None:
        """Persiste un proveedor (crea o actualiza según exista)."""
        ...

    async def delete(self, id: UUID, empresa_id: UUID) -> None:
        """Elimina un proveedor por ID dentro del tenant."""
        ...

    async def has_inventory_parts(self, supplier_id: UUID, empresa_id: UUID) -> bool:
        """Verifica si un proveedor tiene repuestos de inventario asociados."""
        ...
