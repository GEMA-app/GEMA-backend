"""Repositorio de empresas con SQLAlchemy asíncrono."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.company_repository import CompanyRepositoryPort
from app.domain.entities import Company
from app.domain.events import DomainEvent
from app.domain.value_objects import CompanyId, Slug, SubscriptionPlanId
from app.infrastructure.db.models.company import CompanyModel
from app.infrastructure.repositories.base import SqlAlchemyRepository


class SqlAlchemyCompanyRepository(
    SqlAlchemyRepository[CompanyModel, Company, CompanyId], CompanyRepositoryPort
):
    """Implementación en SQLAlchemy para el puerto de repositorio de Empresa."""

    def __init__(
        self, session: AsyncSession, pending_events: list[DomainEvent] | None = None
    ) -> None:
        """Inicializa el repositorio de empresas con la sesión de base de datos.

        Args:
            session: Sesión asíncrona de SQLAlchemy.
            pending_events: Lista para la acumulación de eventos de dominio.
        """
        super().__init__(session, CompanyModel, pending_events)

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
            version=entity.version,
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
            version=model.version,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def get_by_slug(self, slug: Slug) -> Company | None:
        """Busca una empresa por su slug único.

        Args:
            slug: Objeto de valor con el slug de la empresa.

        Returns:
            La entidad Company si fue encontrada; de lo contrario, None.
        """
        stmt = select(CompanyModel).where(CompanyModel.slug == slug.value)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_entity(model)

    async def list_all(self, offset: int, limit: int) -> tuple[list[Company], int]:
        """Lista todas las empresas registradas con paginación.

        Args:
            offset: Número de registros a omitir.
            limit: Número máximo de registros a retornar.

        Returns:
            Una tupla con la lista de empresas encontradas y el conteo total.
        """
        from sqlalchemy import func

        count_stmt = select(func.count(CompanyModel.id))
        count_res = await self.session.execute(count_stmt)
        total = count_res.scalar_one()

        stmt = select(CompanyModel).offset(offset).limit(limit).order_by(CompanyModel.id)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models], total

    async def count_by_plan_id(self, plan_id: SubscriptionPlanId) -> int:
        """Cuenta el número de empresas asociadas a un plan de suscripción.

        Args:
            plan_id: El identificador del plan de suscripción.

        Returns:
            El total de empresas asociadas al plan.
        """
        from sqlalchemy import func

        stmt = select(func.count(CompanyModel.id)).where(CompanyModel.plan_id == plan_id.value)
        result = await self.session.execute(stmt)
        return result.scalar_one()
