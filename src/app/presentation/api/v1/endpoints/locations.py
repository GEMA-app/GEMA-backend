"""Endpoints CRUD de ubicaciones jerárquicas: creación, árbol completo,
obtención, actualización, eliminación y consulta de hijos directos.
"""

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
    empresa_id: str,
    request: CreateLocationRequest,
    current_user: UserResponse = Depends(require_permission(PermissionModule.ADMIN, "create")),
    use_case: CreateLocationUseCase = Depends(get_create_location_use_case),
) -> LocationDocument:
    """Crea una nueva ubicación jerárquica en la empresa.

    Args:
        empresa_id: Identificador de la empresa.
        request: Datos de la ubicación en formato JSON:API.
        current_user: Usuario autenticado con permiso de administración.
        use_case: Caso de uso de creación de ubicación.

    Returns:
        Documento JSON:API con los datos de la ubicación creada.
    """
    dto = CreateLocationDTO(
        nombre=request.data.attributes.nombre,
        tipo=request.data.attributes.tipo.value,
        parent_id=request.data.attributes.parent_id,
        descripcion=request.data.attributes.descripcion,
    )
    res = await use_case.execute(empresa_id, dto)
    return LocationDocument(
        data=LocationResource(
            id=res.id,
            attributes=LocationAttributes(
                empresa_id=res.empresa_id,
                nombre=res.nombre,
                tipo=res.tipo,
                parent_id=res.parent_id,
                descripcion=res.descripcion,
                version=res.version,
            ),
        )
    )


@router.get(
    "",
    response_model=LocationTreeDocument,
    summary="Obtener el árbol jerárquico de ubicaciones",
)
async def get_location_tree(
    empresa_id: str,
    current_user: UserResponse = Depends(require_tenant_read),
    use_case: GetLocationTreeUseCase = Depends(provide_location_tree_use_case),
) -> LocationTreeDocument:
    """Obtiene el árbol jerárquico completo de ubicaciones de la empresa.

    Args:
        empresa_id: Identificador de la empresa.
        current_user: Usuario autenticado con acceso al tenant.
        use_case: Caso de uso de obtención del árbol de ubicaciones.

    Returns:
        Documento JSON:API con la estructura jerárquica de ubicaciones.
    """
    tree = await use_case.execute(empresa_id)

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
    "/{ubicacion_id}",
    response_model=LocationDocument,
    summary="Obtener ubicación por ID",
)
async def get_location(
    empresa_id: str,
    ubicacion_id: str,
    current_user: UserResponse = Depends(require_tenant_read),
    use_case: GetLocationUseCase = Depends(provide_location_use_case),
) -> LocationDocument:
    """Obtiene los detalles de una ubicación por su ID.

    Args:
        empresa_id: Identificador de la empresa.
        ubicacion_id: Identificador único de la ubicación.
        current_user: Usuario autenticado con acceso al tenant.
        use_case: Caso de uso de obtención de ubicación.

    Returns:
        Documento JSON:API con los datos de la ubicación.
    """
    res = await use_case.execute(empresa_id, ubicacion_id)
    return LocationDocument(
        data=LocationResource(
            id=res.id,
            attributes=LocationAttributes(
                empresa_id=res.empresa_id,
                nombre=res.nombre,
                tipo=res.tipo,
                parent_id=res.parent_id,
                descripcion=res.descripcion,
                version=res.version,
            ),
        )
    )


@router.patch(
    "/{ubicacion_id}",
    response_model=LocationDocument,
    summary="Actualizar ubicación",
)
async def update_location(
    empresa_id: str,
    ubicacion_id: str,
    request: UpdateLocationRequest,
    current_user: UserResponse = Depends(require_permission(PermissionModule.ADMIN, "edit")),
    use_case: UpdateLocationUseCase = Depends(get_update_location_use_case),
) -> LocationDocument:
    """Actualiza los datos de una ubicación existente.

    Args:
        empresa_id: Identificador de la empresa.
        ubicacion_id: Identificador único de la ubicación.
        request: Datos actualizados en formato JSON:API.
        current_user: Usuario autenticado con permiso de edición.
        use_case: Caso de uso de actualización de ubicación.

    Returns:
        Documento JSON:API con los datos actualizados de la ubicación.
    """
    attrs = request.data.attributes
    sent = attrs.model_dump(exclude_unset=True)
    dto = UpdateLocationDTO(
        nombre=sent.get("nombre") if "nombre" in sent else None,
        tipo=attrs.tipo.value if ("tipo" in sent and attrs.tipo) else None,
        parent_id=sent.get("parent_id") if "parent_id" in sent else None,
        descripcion=sent.get("descripcion") if "descripcion" in sent else None,
        version=sent.get("version") if "version" in sent else None,
        _fields_set=frozenset(sent.keys()),
    )
    res = await use_case.execute(empresa_id, ubicacion_id, dto)
    return LocationDocument(
        data=LocationResource(
            id=res.id,
            attributes=LocationAttributes(
                empresa_id=res.empresa_id,
                nombre=res.nombre,
                tipo=res.tipo,
                parent_id=res.parent_id,
                descripcion=res.descripcion,
                version=res.version,
            ),
        )
    )


@router.delete(
    "/{ubicacion_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar ubicación",
)
async def delete_location(
    empresa_id: str,
    ubicacion_id: str,
    current_user: UserResponse = Depends(require_permission(PermissionModule.ADMIN, "delete")),
    use_case: DeleteLocationUseCase = Depends(get_delete_location_use_case),
) -> None:
    """Elimina una ubicación de la empresa.

    Args:
        empresa_id: Identificador de la empresa.
        ubicacion_id: Identificador único de la ubicación a eliminar.
        current_user: Usuario autenticado con permiso de eliminación.
        use_case: Caso de uso de eliminación de ubicación.
    """
    await use_case.execute(empresa_id, ubicacion_id)


@router.get(
    "/{ubicacion_id}/hijos",
    response_model=LocationListDocument,
    summary="Obtener ubicaciones hijas directas",
)
async def get_location_children(
    empresa_id: str,
    ubicacion_id: str,
    current_user: UserResponse = Depends(require_tenant_read),
    use_case: GetLocationChildrenUseCase = Depends(provide_location_children_use_case),
) -> LocationListDocument:
    """Obtiene las ubicaciones hijas directas de una ubicación padre.

    Args:
        empresa_id: Identificador de la empresa.
        ubicacion_id: Identificador único de la ubicación padre.
        current_user: Usuario autenticado con acceso al tenant.
        use_case: Caso de uso de obtención de hijos de ubicación.

    Returns:
        Documento JSON:API con la lista de ubicaciones hijas directas.
    """
    children = await use_case.execute(empresa_id, ubicacion_id)
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
                    version=c.version,
                ),
            )
            for c in children
        ]
    )
