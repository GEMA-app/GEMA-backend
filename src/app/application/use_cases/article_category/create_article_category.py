import uuid
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.entities.article_category import ArticleCategory
from app.application.use_cases.article_categories.schemas import CreateCategoryRequest, ArticleCategoryResponse
from app.application.use_cases.article_categories.errors import ArticleCategoryNameExistsError

class CreateArticleCategoryUseCase:
    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(self, empresa_id_str: str, request: CreateCategoryRequest) -> ArticleCategoryResponse:
        empresa_id = uuid.UUID(empresa_id_str)
        async with self.uow:
            existing = await self.uow.article_categories.get_by_name(request.nombre, empresa_id)
            if existing:
                raise ArticleCategoryNameExistsError(f"La categoría '{request.nombre}' ya existe.")
            
            category = ArticleCategory.create(
                id=uuid.uuid4(),
                empresa_id=empresa_id,
                nombre=request.nombre,
                descripcion=request.descripcion
            )
            await self.uow.article_categories.save(category)
            await self.uow.commit()
            return ArticleCategoryResponse(
                id=category.id, empresa_id=category.empresa_id,
                nombre=category.nombre, descripcion=category.descripcion, version=category.version
            )