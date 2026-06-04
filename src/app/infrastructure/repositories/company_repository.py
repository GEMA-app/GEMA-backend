from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.company_repository import CompanyRepositoryPort
from app.domain.entities import Company
from app.domain.value_objects import CompanyId, Slug
from app.infrastructure.db.models.company import CompanyModel
from app.infrastructure.repositories.base import SqlAlchemyRepository


class SqlAlchemyCompanyRepository(
    SqlAlchemyRepository[CompanyModel, Company, CompanyId], CompanyRepositoryPort
):
    """Implementación en SQLAlchemy para el puerto de repositorio de Empresa."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, CompanyModel)

    def _to_model(self, entity: Company) -> CompanyModel:
        return CompanyModel(
            id=entity.id.value,
            nombre=entity.nombre,
            slug=entity.slug.value,
            rif=entity.rif,
            email_contacto=entity.email_contacto,
            estado=entity.estado,
            plan_id=entity.plan_id,
            trial_hasta=entity.trial_hasta,
        )

    def _to_entity(self, model: CompanyModel) -> Company:
        return Company(
            id=CompanyId(model.id),
            nombre=model.nombre,
            slug=Slug(model.slug),
            rif=model.rif,
            email_contacto=model.email_contacto,
            estado=model.estado,
            plan_id=model.plan_id,
            trial_hasta=model.trial_hasta,
        )

    async def get_by_slug(self, slug: Slug) -> Company | None:
        stmt = select(CompanyModel).where(CompanyModel.slug == slug.value)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_entity(model)

    async def list_all(self, offset: int, limit: int) -> tuple[list[Company], int]:
        from sqlalchemy import func

        count_stmt = select(func.count(CompanyModel.id))
        count_res = await self.session.execute(count_stmt)
        total = count_res.scalar_one()

        stmt = select(CompanyModel).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models], total
