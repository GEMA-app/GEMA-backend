import uuid
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.application.use_cases.article_categories.errors import ArticleCategoryNotFoundError

class DeleteArticleCategoryUseCase:
    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(self, empresa_id_str: str, category_id: uuid.UUID) -> None:
        empresa_id = uuid.UUID(empresa_id_str)
        async with self.uow:
            category = await self.uow.article_categories.get_by_id(category_id, empresa_id)
            if not category:
                raise ArticleCategoryNotFoundError("Categoría no encontrada.")
            
            await self.uow.article_categories.delete(category.id, empresa_id)
            await self.uow.commit()