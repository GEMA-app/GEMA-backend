"""Endpoints REST para el CRUD de categorías de artículos del catálogo.

Ruta base: /v1/empresas/{empresa_id}/catalogo/categorias
"""

from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.application.dtos.article_category_dtos import (
    CreateCategoryRequest as CreateCategoryDTO,
)
from app.application.dtos.article_category_dtos import (
    UpdateCategoryRequest as UpdateCategoryDTO,
)
from app.application.dtos.auth_dtos import UserResponse
from app.application.use_cases.article_category.create_article_category import (
    CreateArticleCategoryUseCase,
)
from app.application.use_cases.article_category.delete_article_category import (
    DeleteArticleCategoryUseCase,
)
from app.application.use_cases.article_category.get_article_category_by_id import (
    GetArticleCategoryByIdUseCase,
)
from app.application.use_cases.article_category.list_article_category import (
    ListArticleCategoriesUseCase,
)
from app.application.use_cases.article_category.update_article_category import (
    UpdateArticleCategoryUseCase,
)
from app.composition.container.article_category import (
    get_article_category_by_id_use_case,
    get_create_article_category_use_case,
    get_delete_article_category_use_case,
    get_list_article_categories_use_case,
    get_update_article_category_use_case,
)
from app.domain.enums import PermissionModule
from app.presentation.api.v1.endpoints.dependencies import require_permission
from app.presentation.api.v1.schemas.article_category import (
    ArticleCategoryAttributes,
    ArticleCategoryDocument,
    ArticleCategoryListDocument,
    ArticleCategoryResource,
    CreateCategoryRequest,
    UpdateCategoryRequest,
)

router = APIRouter()


@router.post("", response_model=ArticleCategoryDocument, status_code=status.HTTP_201_CREATED)
async def create_category(
    empresa_id: str,
    payload: CreateCategoryRequest,
    use_case: CreateArticleCategoryUseCase = Depends(
        get_create_article_category_use_case
    ),
    current_user: UserResponse = Depends(
        require_permission(PermissionModule.ADMIN, "create")
    ),
) -> ArticleCategoryDocument:
    """Crea una nueva categoría de artículo en el catálogo de la empresa.

    Args:
        empresa_id: Identificador UUID de la empresa (tenant).
        payload: Datos de la categoría a crear en formato JSON:API.
        current_user: Usuario autenticado con permiso de administración.
        use_case: Caso de uso de creación de categoría.

    Returns:
        Documento JSON:API con la categoría creada.
    """
    dto = CreateCategoryDTO(
        name=payload.data.attributes.name,
        description=payload.data.attributes.description,
    )
    res = await use_case.execute(empresa_id, dto)
    return ArticleCategoryDocument(
        data=ArticleCategoryResource(
            id=str(res.id),
            attributes=ArticleCategoryAttributes(
                empresa_id=str(res.empresa_id),
                name=res.name,
                description=res.description,
                version=res.version,
                articulos_count=res.articulos_count,
            ),
        )
    )


@router.get("", response_model=ArticleCategoryListDocument)
async def list_categories(
    empresa_id: str,
    use_case: ListArticleCategoriesUseCase = Depends(
        get_list_article_categories_use_case
    ),
    current_user: UserResponse = Depends(
        require_permission(PermissionModule.ADMIN, "view")
    ),
) -> ArticleCategoryListDocument:
    """Lista todas las categorías de artículo de la empresa.

    Args:
        empresa_id: Identificador UUID de la empresa (tenant).
        current_user: Usuario autenticado con permiso de administración.
        use_case: Caso de uso de listado de categorías.

    Returns:
        Documento JSON:API con la lista de categorías.
    """
    categories = await use_case.execute(empresa_id)
    return ArticleCategoryListDocument(
        data=[
            ArticleCategoryResource(
                id=str(c.id),
                attributes=ArticleCategoryAttributes(
                    empresa_id=str(c.empresa_id),
                    name=c.name,
                    description=c.description,
                    version=c.version,
                    articulos_count=c.articulos_count,
                ),
            )
            for c in categories
        ]
    )


@router.get("/{categoria_id}", response_model=ArticleCategoryDocument)
async def get_category_by_id(
    empresa_id: str,
    categoria_id: UUID,
    use_case: GetArticleCategoryByIdUseCase = Depends(
        get_article_category_by_id_use_case
    ),
    current_user: UserResponse = Depends(
        require_permission(PermissionModule.ADMIN, "view")
    ),
) -> ArticleCategoryDocument:
    """Obtiene una categoría de artículo por su ID.

    Args:
        empresa_id: Identificador UUID de la empresa (tenant).
        categoria_id: Identificador UUID de la categoría.
        current_user: Usuario autenticado con permiso de administración.
        use_case: Caso de uso de obtención de categoría.

    Returns:
        Documento JSON:API con la categoría solicitada.
    """
    res = await use_case.execute(empresa_id, categoria_id)
    return ArticleCategoryDocument(
        data=ArticleCategoryResource(
            id=str(res.id),
            attributes=ArticleCategoryAttributes(
                empresa_id=str(res.empresa_id),
                name=res.name,
                description=res.description,
                version=res.version,
                articulos_count=res.articulos_count,
            ),
        )
    )


@router.patch("/{categoria_id}", response_model=ArticleCategoryDocument)
async def update_category(
    empresa_id: str,
    categoria_id: UUID,
    payload: UpdateCategoryRequest,
    use_case: UpdateArticleCategoryUseCase = Depends(
        get_update_article_category_use_case
    ),
    current_user: UserResponse = Depends(
        require_permission(PermissionModule.ADMIN, "edit")
    ),
) -> ArticleCategoryDocument:
    """Actualiza parcialmente una categoría de artículo.

    Args:
        empresa_id: Identificador UUID de la empresa (tenant).
        categoria_id: Identificador UUID de la categoría.
        payload: Datos a actualizar en formato JSON:API.
        current_user: Usuario autenticado con permiso de administración.
        use_case: Caso de uso de actualización de categoría.

    Returns:
        Documento JSON:API con la categoría actualizada.
    """
    attrs = payload.data.attributes
    sent = attrs.model_dump(exclude_unset=True)
    dto = UpdateCategoryDTO(
        name=sent.get("name") if "name" in sent else None,
        description=sent.get("description") if "description" in sent else None,
        version=sent.get("version") if "version" in sent else None,
        _fields_set=frozenset(sent.keys()),
    )
    res = await use_case.execute(empresa_id, categoria_id, dto)
    return ArticleCategoryDocument(
        data=ArticleCategoryResource(
            id=str(res.id),
            attributes=ArticleCategoryAttributes(
                empresa_id=str(res.empresa_id),
                name=res.name,
                description=res.description,
                version=res.version,
                articulos_count=res.articulos_count,
            ),
        )
    )


@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    empresa_id: str,
    categoria_id: UUID,
    use_case: DeleteArticleCategoryUseCase = Depends(
        get_delete_article_category_use_case
    ),
    current_user: UserResponse = Depends(
        require_permission(PermissionModule.ADMIN, "delete")
    ),
) -> None:
    """Elimina una categoría de artículo por su ID.

    Args:
        empresa_id: Identificador UUID de la empresa (tenant).
        categoria_id: Identificador UUID de la categoría a eliminar.
        current_user: Usuario autenticado con permiso de administración.
        use_case: Caso de uso de eliminación de categoría.
    """
    await use_case.execute(empresa_id, categoria_id)
