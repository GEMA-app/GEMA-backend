"""Fábricas de dependencias para los casos de uso de empresas."""

from fastapi import Depends

from app.application.ports.unit_of_work import UnitOfWorkPort
from app.application.use_cases.company import (
    CreateCompanyUseCase,
    DeleteCompanyUseCase,
    GetCompanyUseCase,
    UpdateCompanyUseCase,
)
from app.application.use_cases.company.list_company import ListCompaniesUseCase
from app.composition.container.common import get_uow


async def get_create_company_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> CreateCompanyUseCase:
    """Fábrica de dependencias para el caso de uso de creación de empresa."""
    return CreateCompanyUseCase(uow)


async def get_company_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> GetCompanyUseCase:
    """Fábrica de dependencias para el caso de uso de consulta de empresa."""
    return GetCompanyUseCase(uow)


async def get_list_companies_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> ListCompaniesUseCase:
    """Fábrica de dependencias para el caso de uso de listado de empresas."""
    return ListCompaniesUseCase(uow)


async def get_update_company_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> UpdateCompanyUseCase:
    """Fábrica de dependencias para el caso de uso de actualización de empresa."""
    return UpdateCompanyUseCase(uow)


async def get_delete_company_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> DeleteCompanyUseCase:
    """Fábrica de dependencias para el caso de uso de eliminación de empresa."""
    return DeleteCompanyUseCase(uow)
