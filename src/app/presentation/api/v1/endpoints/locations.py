from typing import Any

from fastapi import APIRouter, Depends, status

from app.application.dtos.auth_dtos import UserResponse
from app.application.dtos.location_dtos import (
    CreateLocationRequest as CreateLocationDTO,
)
from app.application.dtos.location_dtos import (
    LocationTreeResponse,
)
from app.application.dtos.location_dtos import (
    UpdateLocationRequest as UpdateLocationDTO,
)
from app.application.use_cases.location import (
    CreateLocationUseCase,
    DeleteLocationUseCase,
    GetLocationChildrenUseCase,
    GetLocationTreeUseCase,
    GetLocationUseCase,
    UpdateLocationUseCase,
)
from app.composition.container import (
    get_create_location_use_case,
    get_delete_location_use_case,
    get_update_location_use_case,
    provide_location_children_use_case,
    provide_location_tree_use_case,
    provide_location_use_case,
)
from app.domain.enums import PermissionModule
from app.presentation.api.v1.endpoints.dependencies import (
    require_permission,
    require_tenant_read,
)
from app.presentation.api.v1.schemas.location import (
    CreateLocationRequest,
    LocationAttributes,
    LocationDocument,
    LocationListDocument,
    LocationResource,
    LocationTreeAttributes,
    LocationTreeDocument,
    LocationTreeResource,
    UpdateLocationRequest,
)

router = APIRouter()


@router.post(
    "",
    response_model=LocationDocument,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una nueva ubicación",
)
async def create_location(
    company_id: str,
    request: CreateLocationRequest,
    current_user: Any = Depends(require_permission(PermissionModule.ADMIN, "create")),
    use_case: CreateLocationUseCase = Depends(get_create_location_use_case),
) -> LocationDocument:
    dto = CreateLocationDTO(
        nombre=request.data.attributes.nombre,
        tipo=request.data.attributes.tipo,
        parent_id=request.data.attributes.parent_id,
        descripcion=request.data.attributes.descripcion,
    )
    res = await use_case.execute(company_id, dto)
    return LocationDocument(
        data=LocationResource(
            id=res.id,
            attributes=LocationAttributes(
                empresa_id=res.empresa_id,
                nombre=res.nombre,
                tipo=res.tipo,
                parent_id=res.parent_id,
                descripcion=res.descripcion,
            ),
        )
    )


@router.get(
    "",
    response_model=LocationTreeDocument,
    summary="Obtener el árbol jerárquico de ubicaciones",
)
async def get_location_tree(
    company_id: str,
    current_user: UserResponse = Depends(require_tenant_read),
    use_case: GetLocationTreeUseCase = Depends(provide_location_tree_use_case),
) -> LocationTreeDocument:
    tree = await use_case.execute(company_id)

    def map_tree_node(node: LocationTreeResponse) -> LocationTreeResource:
        return LocationTreeResource(
            id=node.id,
            attributes=LocationTreeAttributes(
                nombre=node.nombre,
                tipo=node.tipo,
                descripcion=node.descripcion,
                children=[map_tree_node(child) for child in node.children],
            ),
        )

    return LocationTreeDocument(data=[map_tree_node(root) for root in tree])


@router.get(
    "/{location_id}",
    response_model=LocationDocument,
    summary="Obtener ubicación por ID",
)
async def get_location(
    company_id: str,
    location_id: str,
    current_user: UserResponse = Depends(require_tenant_read),
    use_case: GetLocationUseCase = Depends(provide_location_use_case),
) -> LocationDocument:
    res = await use_case.execute(company_id, location_id)
    return LocationDocument(
        data=LocationResource(
            id=res.id,
            attributes=LocationAttributes(
                empresa_id=res.empresa_id,
                nombre=res.nombre,
                tipo=res.tipo,
                parent_id=res.parent_id,
                descripcion=res.descripcion,
            ),
        )
    )


@router.patch(
    "/{location_id}",
    response_model=LocationDocument,
    summary="Actualizar ubicación",
)
async def update_location(
    company_id: str,
    location_id: str,
    request: UpdateLocationRequest,
    current_user: Any = Depends(require_permission(PermissionModule.ADMIN, "edit")),
    use_case: UpdateLocationUseCase = Depends(get_update_location_use_case),
) -> LocationDocument:
    dto = UpdateLocationDTO(
        nombre=request.data.attributes.nombre,
        tipo=request.data.attributes.tipo,
        parent_id=request.data.attributes.parent_id,
        descripcion=request.data.attributes.descripcion,
    )
    res = await use_case.execute(company_id, location_id, dto)
    return LocationDocument(
        data=LocationResource(
            id=res.id,
            attributes=LocationAttributes(
                empresa_id=res.empresa_id,
                nombre=res.nombre,
                tipo=res.tipo,
                parent_id=res.parent_id,
                descripcion=res.descripcion,
            ),
        )
    )


@router.delete(
    "/{location_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar ubicación",
)
async def delete_location(
    company_id: str,
    location_id: str,
    current_user: Any = Depends(require_permission(PermissionModule.ADMIN, "delete")),
    use_case: DeleteLocationUseCase = Depends(get_delete_location_use_case),
) -> None:
    await use_case.execute(company_id, location_id)


@router.get(
    "/{location_id}/children",
    response_model=LocationListDocument,
    summary="Obtener ubicaciones hijas directas",
)
async def get_location_children(
    company_id: str,
    location_id: str,
    current_user: UserResponse = Depends(require_tenant_read),
    use_case: GetLocationChildrenUseCase = Depends(provide_location_children_use_case),
) -> LocationListDocument:
    children = await use_case.execute(company_id, location_id)
    return LocationListDocument(
        data=[
            LocationResource(
                id=c.id,
                attributes=LocationAttributes(
                    empresa_id=c.empresa_id,
                    nombre=c.nombre,
                    tipo=c.tipo,
                    parent_id=c.parent_id,
                    descripcion=c.descripcion,
                ),
            )
            for c in children
        ]
    )
