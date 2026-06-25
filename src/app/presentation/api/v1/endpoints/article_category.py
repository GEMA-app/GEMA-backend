from fastapi import APIRouter, Depends, status
from uuid import UUID
from app.presentation.api.v1.schemas.article_category import (
    ArticleCategoryDocument, ArticleCategoryListDocument, 
    ArticleCategoryResource, ArticleCategoryAttributes
)
from app.application.dtos.article_category_dtos import CreateCategoryRequest, UpdateCategoryRequest
from app.application.use_cases.article_categories.create_article_category import CreateArticleCategoryUseCase
from app.application.use_cases.article_categories.get_article_category_by_id import GetArticleCategoryByIdUseCase
from app.application.use_cases.article_categories.get_all_article_categories import GetAllArticleCategoriesUseCase
from app.application.use_cases.article_categories.update_article_category import UpdateArticleCategoryUseCase
from app.application.use_cases.article_categories.delete_article_category import DeleteArticleCategoryUseCase
from app.presentation.api.v1.dependencies import (
    get_create_category_use_case, get_get_category_by_id_use_case,
    get_get_all_categories_use_case, get_update_category_use_case,
    get_delete_category_use_case, require_permission
)

router = APIRouter(prefix="/v1/empresas/{empresa_id}/catalogo/categorias")

@router.post("", response_model=ArticleCategoryDocument, status_code=status.HTTP_201_CREATED)
async def create_category(
    empresa_id: str,
    payload: CreateCategoryRequest,
    use_case: CreateArticleCategoryUseCase = Depends(get_create_category_use_case),
    current_user = Depends(require_permission("administracion:create"))
) -> ArticleCategoryDocument:
    res = await use_case.execute(empresa_id, payload)
    return ArticleCategoryDocument(
        data=ArticleCategoryResource(
            id=str(res.id),
            attributes=ArticleCategoryAttributes(
                empresa_id=str(res.empresa_id), nombre=res.nombre, descripcion=res.descripcion, version=res.version
            )
        )
    )

@router.get("", response_model=ArticleCategoryListDocument)
async def get_all_categories(
    empresa_id: str,
    use_case: GetAllArticleCategoriesUseCase = Depends(get_get_all_categories_use_case),
    current_user = Depends(require_permission("administracion:view"))
) -> ArticleCategoryListDocument:
    categories = await use_case.execute(empresa_id)
    return ArticleCategoryListDocument(
        data=[
            ArticleCategoryResource(
                id=str(c.id),
                attributes=ArticleCategoryAttributes(
                    empresa_id=str(c.empresa_id), nombre=c.nombre, descripcion=c.descripcion, version=c.version
                )
            ) for c in categories
        ]
    )

@router.get("/{categoria_id}", response_model=ArticleCategoryDocument)
async def get_category_by_id(
    empresa_id: str,
    categoria_id: UUID,
    use_case: GetArticleCategoryByIdUseCase = Depends(get_get_category_by_id_use_case),
    current_user = Depends(require_permission("administracion:view"))
) -> ArticleCategoryDocument:
    res = await use_case.execute(empresa_id, categoria_id)
    return ArticleCategoryDocument(
        data=ArticleCategoryResource(
            id=str(res.id),
            attributes=ArticleCategoryAttributes(
                empresa_id=str(res.empresa_id), nombre=res.nombre, descripcion=res.descripcion, version=res.version
            )
        )
    )

@router.patch("/{categoria_id}", response_model=ArticleCategoryDocument)
async def update_category(
    empresa_id: str,
    categoria_id: UUID,
    payload: UpdateCategoryRequest,
    use_case: UpdateArticleCategoryUseCase = Depends(get_update_category_use_case),
    current_user = Depends(require_permission("administracion:edit"))
) -> ArticleCategoryDocument:
    res = await use_case.execute(empresa_id, categoria_id, payload)
    return ArticleCategoryDocument(
        data=ArticleCategoryResource(
            id=str(res.id),
            attributes=ArticleCategoryAttributes(
                empresa_id=str(res.empresa_id), nombre=res.nombre, descripcion=res.descripcion, version=res.version
            )
        )
    )

@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    empresa_id: str,
    categoria_id: UUID,
    use_case: DeleteArticleCategoryUseCase = Depends(get_delete_category_use_case),
    current_user = Depends(require_permission("administracion:delete"))
):
    await use_case.execute(empresa_id, categoria_id)