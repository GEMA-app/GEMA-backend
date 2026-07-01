"""Caso de uso para create company."""

from app.application.dtos.company_dtos import CompanyResponse, CreateCompanyRequest
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.entities import Company
from app.domain.exceptions import CompanySlugExistsError
from app.domain.value_objects import Slug


class CreateCompanyUseCase:
    """Caso de uso para registrar una nueva empresa."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(self, request: CreateCompanyRequest) -> CompanyResponse:
        """Registra una nueva empresa."""
        slug_val = request.slug or Slug.from_name(request.nombre).value
        slug = Slug(slug_val)

        async with self.uow:
            existing = await self.uow.companies.get_by_slug(slug)
            if existing:
                raise CompanySlugExistsError(f"La empresa con el slug '{slug.value}' ya existe.")

            company = Company.create(
                nombre=request.nombre,
                slug=slug,
                rif=request.rif,
                email_contacto=request.email_contacto,
                plan_id=request.plan_id,
                trial_hasta=request.trial_hasta,
            )
            await self.uow.companies.save(company)
            await self.uow.commit()

            return CompanyResponse(
                id=str(company.id),
                nombre=company.nombre,
                slug=company.slug.value,
                rif=company.rif,
                email_contacto=company.email_contacto,
                estado=company.estado.value,
                plan_id=str(company.plan_id) if company.plan_id else None,
                trial_hasta=company.trial_hasta.isoformat() if company.trial_hasta else None,
                version=company.version,
            )
