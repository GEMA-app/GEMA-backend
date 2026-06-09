from app.application.dtos.company_dtos import CompanyResponse
from app.application.ports.unit_of_work import UnitOfWorkPort


class ListCompaniesUseCase:
    """Caso de uso para listar empresas paginadas."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(
        self, offset: int, limit: int, company_id: str | None = None
    ) -> tuple[list[CompanyResponse], int]:
        async with self.uow:
            if company_id is not None:
                from app.domain.value_objects import CompanyId
                company = await self.uow.companies.get_by_id(
                    CompanyId.from_string(company_id)
                )
                if not company:
                    return [], 0
                dto = CompanyResponse(
                    id=str(company.id),
                    nombre=company.nombre,
                    slug=company.slug.value,
                    rif=company.rif,
                    email_contacto=company.email_contacto,
                    estado=company.estado.value,
                    plan_id=str(company.plan_id) if company.plan_id else None,
                    trial_hasta=company.trial_hasta.isoformat() if company.trial_hasta else None,
                )
                return [dto], 1

            companies, total = await self.uow.companies.list_all(offset, limit)
            responses = [
                CompanyResponse(
                    id=str(c.id),
                    nombre=c.nombre,
                    slug=c.slug.value,
                    rif=c.rif,
                    email_contacto=c.email_contacto,
                    estado=c.estado.value,
                    plan_id=str(c.plan_id) if c.plan_id else None,
                    trial_hasta=c.trial_hasta.isoformat() if c.trial_hasta else None,
                )
                for c in companies
            ]
            return responses, total
