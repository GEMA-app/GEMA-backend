"""Fábricas de dependencias para los casos de uso de empresas."""

from fastapi import Depends

from app.application.ports.unit_of_work import UnitOfWorkPort
from app.application.use_cases.company import (
    CreateCompanyUseCase,
    DeleteCompanyUseCase,
    GetCompanyUseCase,
    ListCompaniesUseCase,
    UpdateCompanyUseCase,
)
from app.composition.container.common import get_uow


async def get_create_company_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> CreateCompanyUseCase:
    return CreateCompanyUseCase(uow)


async def provide_company_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> GetCompanyUseCase:
    return GetCompanyUseCase(uow)


async def get_list_companies_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> ListCompaniesUseCase:
    return ListCompaniesUseCase(uow)


async def get_update_company_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> UpdateCompanyUseCase:
    return UpdateCompanyUseCase(uow)


async def get_delete_company_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> DeleteCompanyUseCase:
    return DeleteCompanyUseCase(uow)
