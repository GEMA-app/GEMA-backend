import uuid
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.application.use_cases.article_categories.schemas import UpdateCategoryRequest, ArticleCategoryResponse
from app.application.use_cases.article_categories.errors import ArticleCategoryNotFoundError, ArticleCategoryNameExistsError

class UpdateArticleCategoryUseCase:
    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(self, empresa_id_str: str, category_id: uuid.UUID, request: UpdateCategoryRequest) -> ArticleCategoryResponse:
        empresa_id = uuid.UUID(empresa_id_str)
        async with self.uow:
            category = await self.uow.article_categories.get_by_id(category_id, empresa_id)
            if not category:
                raise ArticleCategoryNotFoundError("Categoría no encontrada.")
            
            if request.nombre and request.nombre != category.nombre:
                existing = await self.uow.article_categories.get_by_name(request.nombre, empresa_id)
                if existing:
                    raise ArticleCategoryNameExistsError(f"El nombre '{request.nombre}' ya está en uso.")
                category.change_nombre(request.nombre) # Usamos método de negocio de la entidad
                
            if request.descripcion is not None:
                category.change_descripcion(request.descripcion)

            await self.uow.article_categories.save(category)
            await self.uow.commit()
            return ArticleCategoryResponse(
                id=category.id, empresa_id=category.empresa_id,
                nombre=category.nombre, descripcion=category.descripcion, version=category.version
            )