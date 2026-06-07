from typing import Any

from fastapi import APIRouter, Depends, status

from app.application.dtos.company_dtos import (
    CreateCompanyRequest as CreateCompanyDTO,
)
from app.application.dtos.company_dtos import (
    UpdateCompanyRequest as UpdateCompanyDTO,
)
from app.application.use_cases.company import (
    CreateCompanyUseCase,
    DeleteCompanyUseCase,
    GetCompanyUseCase,
    ListCompaniesUseCase,
    UpdateCompanyUseCase,
)
from app.composition.container import (
    get_create_company_use_case,
    get_delete_company_use_case,
    get_list_companies_use_case,
    get_update_company_use_case,
    provide_company_use_case,
)
from app.domain.enums import PermissionModule
from app.presentation.api.v1.endpoints.dependencies import (
    get_current_active_user,
    require_permission,
)
from app.presentation.api.v1.schemas.company import (
    CompanyAttributes,
    CompanyDocument,
    CompanyListDocument,
    CompanyResource,
    CreateCompanyRequest,
    UpdateCompanyRequest,
)

router = APIRouter()


@router.post(
    "",
    response_model=CompanyDocument,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nueva empresa",
)
async def create_company(
    request: CreateCompanyRequest,
    current_user: Any = Depends(require_permission(PermissionModule.ADMIN, "create")),
    use_case: CreateCompanyUseCase = Depends(get_create_company_use_case),
) -> CompanyDocument:
    dto = CreateCompanyDTO(
        nombre=request.data.attributes.nombre,
        slug=request.data.attributes.slug,
        rif=request.data.attributes.rif,
        email_contacto=request.data.attributes.email_contacto,
    )
    res = await use_case.execute(dto)
    return CompanyDocument(
        data=CompanyResource(
            id=res.id,
            attributes=CompanyAttributes(
                nombre=res.nombre,
                slug=res.slug,
                estado=res.estado,
                rif=res.rif,
                email_contacto=res.email_contacto,
                plan_id=res.plan_id,
                trial_hasta=res.trial_hasta,
            ),
        )
    )


@router.get(
    "",
    response_model=CompanyListDocument,
    summary="Listar empresas",
)
async def list_companies(
    offset: int = 0,
    limit: int = 10,
    current_user: Any = Depends(get_current_active_user),
    use_case: ListCompaniesUseCase = Depends(get_list_companies_use_case),
) -> CompanyListDocument:
    companies, total = await use_case.execute(offset, limit)
    return CompanyListDocument(
        data=[
            CompanyResource(
                id=c.id,
                attributes=CompanyAttributes(
                    nombre=c.nombre,
                    slug=c.slug,
                    estado=c.estado,
                    rif=c.rif,
                    email_contacto=c.email_contacto,
                    plan_id=c.plan_id,
                    trial_hasta=c.trial_hasta,
                ),
            )
            for c in companies
        ],
        meta={"total": total},
    )


@router.get(
    "/{id}",
    response_model=CompanyDocument,
    summary="Obtener empresa por ID",
)
async def get_company(
    id: str,
    current_user: Any = Depends(get_current_active_user),
    use_case: GetCompanyUseCase = Depends(provide_company_use_case),
) -> CompanyDocument:
    res = await use_case.execute(id)
    return CompanyDocument(
        data=CompanyResource(
            id=res.id,
            attributes=CompanyAttributes(
                nombre=res.nombre,
                slug=res.slug,
                estado=res.estado,
                rif=res.rif,
                email_contacto=res.email_contacto,
                plan_id=res.plan_id,
                trial_hasta=res.trial_hasta,
            ),
        )
    )


@router.patch(
    "/{id}",
    response_model=CompanyDocument,
    summary="Actualizar empresa",
)
async def update_company(
    id: str,
    request: UpdateCompanyRequest,
    current_user: Any = Depends(require_permission(PermissionModule.ADMIN, "edit")),
    use_case: UpdateCompanyUseCase = Depends(get_update_company_use_case),
) -> CompanyDocument:
    dto = UpdateCompanyDTO(
        nombre=request.data.attributes.nombre,
        rif=request.data.attributes.rif,
        email_contacto=request.data.attributes.email_contacto,
        estado=request.data.attributes.estado,
    )
    res = await use_case.execute(id, dto)
    return CompanyDocument(
        data=CompanyResource(
            id=res.id,
            attributes=CompanyAttributes(
                nombre=res.nombre,
                slug=res.slug,
                estado=res.estado,
                rif=res.rif,
                email_contacto=res.email_contacto,
                plan_id=res.plan_id,
                trial_hasta=res.trial_hasta,
            ),
        )
    )


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar empresa",
)
async def delete_company(
    id: str,
    current_user: Any = Depends(require_permission(PermissionModule.ADMIN, "delete")),
    use_case: DeleteCompanyUseCase = Depends(get_delete_company_use_case),
) -> None:
    await use_case.execute(id)
