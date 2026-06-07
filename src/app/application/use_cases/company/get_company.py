from app.application.dtos.company_dtos import CompanyResponse
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.exceptions import CompanyNotFoundError
from app.domain.value_objects import CompanyId


class GetCompanyUseCase:
    """Caso de uso para obtener una empresa por su ID."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(self, company_id_str: str) -> CompanyResponse:
        company_id = CompanyId.from_string(company_id_str)
        async with self.uow:
            company = await self.uow.companies.get_by_id(company_id)
            if not company:
                raise CompanyNotFoundError(f"La empresa con ID '{company_id_str}' no existe.")

            return CompanyResponse(
                id=str(company.id),
                nombre=company.nombre,
                slug=company.slug.value,
                rif=company.rif,
                email_contacto=company.email_contacto,
                estado=company.estado.value,
                plan_id=str(company.plan_id) if company.plan_id else None,
                trial_hasta=company.trial_hasta.isoformat() if company.trial_hasta else None,
            )
