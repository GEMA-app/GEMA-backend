import uuid
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.application.use_cases.article_categories.schemas import ArticleCategoryResponse
from app.application.use_cases.article_categories.errors import ArticleCategoryNotFoundError

class GetArticleCategoryByIdUseCase:
    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(self, empresa_id_str: str, category_id: uuid.UUID) -> ArticleCategoryResponse:
        empresa_id = uuid.UUID(empresa_id_str)
        async with self.uow:
            category = await self.uow.article_categories.get_by_id(category_id, empresa_id)
            if not category:
                raise ArticleCategoryNotFoundError("Categoría de catálogo no encontrada.")
            return ArticleCategoryResponse(
                id=category.id, empresa_id=category.empresa_id,
                nombre=category.nombre, descripcion=category.descripcion, version=category.version
            )