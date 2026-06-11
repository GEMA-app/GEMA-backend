from typing import Any

from fastapi import APIRouter, Depends, status

from app.application.dtos.auth_dtos import UserResponse
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
    require_platform_permission,
    require_tenant_read,
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
    current_user: UserResponse = Depends(require_platform_permission(PermissionModule.ADMIN, "create")),
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
                version=res.version,
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
    companies, total = await use_case.execute(offset, limit, company_id=current_user.empresa_id)
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
                    version=c.version,
                ),
            )
            for c in companies
        ],
        meta={"total": total},
    )


@router.get(
    "/{empresa_id}",
    response_model=CompanyDocument,
    summary="Obtener empresa por ID",
)
async def get_company(
    empresa_id: str,
    current_user: UserResponse = Depends(require_tenant_read),
    use_case: GetCompanyUseCase = Depends(provide_company_use_case),
) -> CompanyDocument:
    res = await use_case.execute(empresa_id)
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
                version=res.version,
            ),
        )
    )


@router.patch(
    "/{empresa_id}",
    response_model=CompanyDocument,
    summary="Actualizar empresa",
)
async def update_company(
    empresa_id: str,
    request: UpdateCompanyRequest,
    current_user: Any = Depends(require_permission(PermissionModule.ADMIN, "edit")),
    use_case: UpdateCompanyUseCase = Depends(get_update_company_use_case),
) -> CompanyDocument:
    attrs = request.data.attributes
    sent = attrs.model_dump(exclude_unset=True)
    dto = UpdateCompanyDTO(
        nombre=sent.get("nombre") if "nombre" in sent else None,
        rif=sent.get("rif") if "rif" in sent else None,
        email_contacto=sent.get("email_contacto") if "email_contacto" in sent else None,
        estado=attrs.estado.value if ("estado" in sent and attrs.estado) else None,
        version=sent.get("version") if "version" in sent else None,
        _fields_set=frozenset(sent.keys()),
    )
    res = await use_case.execute(empresa_id, dto)
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
                version=res.version,
            ),
        )
    )


@router.delete(
    "/{empresa_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar empresa",
)
async def delete_company(
    empresa_id: str,
    current_user: Any = Depends(require_permission(PermissionModule.ADMIN, "delete")),
    use_case: DeleteCompanyUseCase = Depends(get_delete_company_use_case),
) -> None:
    await use_case.execute(empresa_id)
