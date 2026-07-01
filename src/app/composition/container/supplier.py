"""Fábricas de dependencias para el módulo Supplier (Proveedores)."""

from fastapi import Depends

from app.application.ports.unit_of_work import UnitOfWorkPort
from app.application.use_cases.supplier.create_supplier import CreateSupplierUseCase
from app.application.use_cases.supplier.delete_supplier import DeleteSupplierUseCase
from app.application.use_cases.supplier.get_supplier import GetSupplierUseCase
from app.application.use_cases.supplier.list_suppliers import ListSuppliersUseCase
from app.application.use_cases.supplier.update_supplier import UpdateSupplierUseCase
from app.composition.container.common import get_uow


async def get_create_supplier_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> CreateSupplierUseCase:
    """Fábrica de dependencias para el caso de uso de creación de proveedor.

    Args:
        uow: Unidad de trabajo inyectada.

    Returns:
        Instancia del caso de uso CreateSupplierUseCase.
    """
    return CreateSupplierUseCase(uow=uow)


async def get_get_supplier_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> GetSupplierUseCase:
    """Fábrica de dependencias para el caso de uso de consulta de proveedor.

    Args:
        uow: Unidad de trabajo inyectada.

    Returns:
        Instancia del caso de uso GetSupplierUseCase.
    """
    return GetSupplierUseCase(uow=uow)


async def get_list_suppliers_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> ListSuppliersUseCase:
    """Fábrica de dependencias para el caso de uso de listado de proveedores.

    Args:
        uow: Unidad de trabajo inyectada.

    Returns:
        Instancia del caso de uso ListSuppliersUseCase.
    """
    return ListSuppliersUseCase(uow=uow)


async def get_update_supplier_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> UpdateSupplierUseCase:
    """Fábrica de dependencias para el caso de uso de actualización de proveedor.

    Args:
        uow: Unidad de trabajo inyectada.

    Returns:
        Instancia del caso de uso UpdateSupplierUseCase.
    """
    return UpdateSupplierUseCase(uow=uow)


async def get_delete_supplier_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> DeleteSupplierUseCase:
    """Fábrica de dependencias para el caso de uso de eliminación de proveedor.

    Args:
        uow: Unidad de trabajo inyectada.

    Returns:
        Instancia del caso de uso DeleteSupplierUseCase.
    """
    return DeleteSupplierUseCase(uow=uow)
