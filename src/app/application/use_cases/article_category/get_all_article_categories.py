import uuid
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.application.use_cases.article_categories.schemas import ArticleCategoryResponse

class GetAllArticleCategoriesUseCase:
    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(self, empresa_id_str: str) -> list[ArticleCategoryResponse]:
        empresa_id = uuid.UUID(empresa_id_str)
        async with self.uow:
            categories = await self.uow.article_categories.get_all_by_empresa(empresa_id)
            return [
                ArticleCategoryResponse(
                    id=c.id, empresa_id=c.empresa_id,
                    nombre=c.nombre, descripcion=c.descripcion, version=c.version
                )
                for c in categories
            ]