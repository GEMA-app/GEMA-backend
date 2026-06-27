"""Endpoints CRUD de artículos de catálogo: creación, listado,
obtención, actualización y eliminación.
"""

from fastapi import APIRouter, Depends, Query, status

from app.application.dtos.auth_dtos import UserResponse
from app.application.dtos.catalog_article_dtos import (
    CreateCatalogArticleRequest as CreateCatalogArticleDTO,
)
from app.application.dtos.catalog_article_dtos import (
    UpdateCatalogArticleRequest as UpdateCatalogArticleDTO,
)
from app.application.use_cases.catalog_article import (
    CreateCatalogArticleUseCase,
    DeleteCatalogArticleUseCase,
    GetCatalogArticleUseCase,
    UpdateCatalogArticleUseCase,
)
from app.application.use_cases.catalog_article.list_catalog_articles import (
    ListCatalogArticlesUseCase,
)
from app.composition.container import (
    get_catalog_article_use_case,
    get_create_catalog_article_use_case,
    get_delete_catalog_article_use_case,
    get_list_catalog_articles_use_case,
    get_update_catalog_article_use_case,
)
from app.domain.enums import PermissionModule
from app.presentation.api.v1.endpoints.dependencies import (
    require_permission,
    require_tenant_read,
)
from app.presentation.api.v1.schemas.catalog_articles import (
    CatalogArticleAttributes,
    CatalogArticleDocument,
    CatalogArticleListDocument,
    CatalogArticleResource,
    CreateCatalogArticleRequest,
    UpdateCatalogArticleRequest,
)

router = APIRouter()


@router.post(
    "",
    response_model=CatalogArticleDocument,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo artículo de catálogo",
)
async def create_catalog_article(
    empresa_id: str,
    request: CreateCatalogArticleRequest,
    current_user: UserResponse = Depends(
        require_permission(PermissionModule.ADMIN, "create")
    ),
    use_case: CreateCatalogArticleUseCase = Depends(
        get_create_catalog_article_use_case
    ),
) -> CatalogArticleDocument:
    """Crea un nuevo artículo de catálogo en la empresa.

    Args:
        empresa_id: Identificador de la empresa.
        request: Datos del artículo en formato JSON:API.
        current_user: Usuario autenticado (validado por RBAC).
        use_case: Caso de uso de creación inyectado por composición.

    Returns:
        Documento JSON:API con el artículo creado.
    """
    dto = CreateCatalogArticleDTO(
        category_id=request.data.attributes.category_id,
        name=request.data.attributes.name,
        description=request.data.attributes.description,
        manufacturer=request.data.attributes.manufacturer,
        model=request.data.attributes.model,
        unit_of_measure=request.data.attributes.unit_of_measure,
    )
    result = await use_case.execute(empresa_id, dto)
    return CatalogArticleDocument(
        data=CatalogArticleResource(
            type="catalog-articles",
            id=result.id,
            attributes=CatalogArticleAttributes(
                empresa_id=result.empresa_id,
                category_id=result.category_id,
                name=result.name,
                description=result.description,
                manufacturer=result.manufacturer,
                model=result.model,
                unit_of_measure=result.unit_of_measure,
            ),
        ),
    )


@router.get(
    "",
    response_model=CatalogArticleListDocument,
    summary="Listar artículos de catálogo",
)
async def list_catalog_articles(
    empresa_id: str,
    offset: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(20, ge=1, le=100, description="Máximo de registros"),
    category_id: str | None = Query(None, description="Filtrar por categoría"),
    search: str | None = Query(None, description="Búsqueda por nombre"),
    current_user: UserResponse = Depends(require_tenant_read),
    use_case: ListCatalogArticlesUseCase = Depends(
        get_list_catalog_articles_use_case
    ),
) -> CatalogArticleListDocument:
    """Lista los artículos de catálogo de una empresa.

    Args:
        empresa_id: Identificador de la empresa.
        offset: Número de registros a saltar.
        limit: Máximo de registros a retornar.
        category_id: Filtrar por ID de categoría.
        search: Búsqueda textual por nombre.
        current_user: Usuario autenticado (validación de tenant).
        use_case: Caso de uso de listado inyectado por composición.

    Returns:
        Documento JSON:API con la lista de artículos.
    """
    results, total = await use_case.execute(
        empresa_id,
        offset=offset,
        limit=limit,
        category_id=category_id,
        search=search,
    )
    return CatalogArticleListDocument(
        data=[
            CatalogArticleResource(
                type="catalog-articles",
                id=r.id,
                attributes=CatalogArticleAttributes(
                    empresa_id=r.empresa_id,
                    category_id=r.category_id,
                    name=r.name,
                    description=r.description,
                    manufacturer=r.manufacturer,
                    model=r.model,
                    unit_of_measure=r.unit_of_measure,
                ),
            )
            for r in results
        ],
        meta={"total": total} if total else None,
    )


@router.get(
    "/{articulo_id}",
    response_model=CatalogArticleDocument,
    summary="Obtener un artículo de catálogo",
)
async def get_catalog_article(
    empresa_id: str,
    articulo_id: str,
    current_user: UserResponse = Depends(require_tenant_read),
    use_case: GetCatalogArticleUseCase = Depends(get_catalog_article_use_case),
) -> CatalogArticleDocument:
    """Obtiene un artículo de catálogo por su ID.

    Args:
        empresa_id: Identificador de la empresa.
        articulo_id: Identificador del artículo.
        current_user: Usuario autenticado (validación de tenant).
        use_case: Caso de uso de consulta inyectado por composición.

    Returns:
        Documento JSON:API con el artículo solicitado.
    """
    result = await use_case.execute(empresa_id, articulo_id)
    return CatalogArticleDocument(
        data=CatalogArticleResource(
            type="catalog-articles",
            id=result.id,
            attributes=CatalogArticleAttributes(
                empresa_id=result.empresa_id,
                category_id=result.category_id,
                name=result.name,
                description=result.description,
                manufacturer=result.manufacturer,
                model=result.model,
                unit_of_measure=result.unit_of_measure,
            ),
        ),
    )


@router.patch(
    "/{articulo_id}",
    response_model=CatalogArticleDocument,
    summary="Actualizar un artículo de catálogo",
)
async def update_catalog_article(
    empresa_id: str,
    articulo_id: str,
    request: UpdateCatalogArticleRequest,
    current_user: UserResponse = Depends(
        require_permission(PermissionModule.ADMIN, "edit")
    ),
    use_case: UpdateCatalogArticleUseCase = Depends(
        get_update_catalog_article_use_case
    ),
) -> CatalogArticleDocument:
    """Actualiza parcialmente un artículo de catálogo.

    Args:
        empresa_id: Identificador de la empresa.
        articulo_id: Identificador del artículo.
        request: Datos parciales del artículo.
        current_user: Usuario autenticado (validado por RBAC).
        use_case: Caso de uso de actualización inyectado por composición.

    Returns:
        Documento JSON:API con el artículo actualizado.
    """
    attrs = request.data.attributes
    sent = attrs.model_dump(exclude_unset=True)
    dto = UpdateCatalogArticleDTO(
        category_id=sent.get("category_id") if "category_id" in sent else None,
        name=sent.get("name") if "name" in sent else None,
        description=sent.get("description") if "description" in sent else None,
        manufacturer=sent.get("manufacturer") if "manufacturer" in sent else None,
        model=sent.get("model") if "model" in sent else None,
        unit_of_measure=sent.get("unit_of_measure") if "unit_of_measure" in sent else None,
        _fields_set=frozenset(sent.keys()),
    )
    result = await use_case.execute(empresa_id, articulo_id, dto)
    return CatalogArticleDocument(
        data=CatalogArticleResource(
            type="catalog-articles",
            id=result.id,
            attributes=CatalogArticleAttributes(
                empresa_id=result.empresa_id,
                category_id=result.category_id,
                name=result.name,
                description=result.description,
                manufacturer=result.manufacturer,
                model=result.model,
                unit_of_measure=result.unit_of_measure,
            ),
        ),
    )


@router.delete(
    "/{articulo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un artículo de catálogo",
)
async def delete_catalog_article(
    empresa_id: str,
    articulo_id: str,
    current_user: UserResponse = Depends(
        require_permission(PermissionModule.ADMIN, "delete")
    ),
    use_case: DeleteCatalogArticleUseCase = Depends(
        get_delete_catalog_article_use_case
    ),
) -> None:
    """Elimina un artículo de catálogo.

    Args:
        empresa_id: Identificador de la empresa.
        articulo_id: Identificador del artículo a eliminar.
        current_user: Usuario autenticado (validado por RBAC).
        use_case: Caso de uso de eliminación inyectado por composición.
    """
    await use_case.execute(empresa_id, articulo_id)
