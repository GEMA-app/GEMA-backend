from app.application.dtos.company_dtos import CompanyResponse
from app.application.ports.unit_of_work import UnitOfWorkPort


class ListCompaniesUseCase:
    """Caso de uso para listar empresas paginadas."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(self, offset: int, limit: int) -> tuple[list[CompanyResponse], int]:
        async with self.uow:
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
                    trial_hasta=c.trial_hasta.isoformat() if c.trial_hasta else None
                )
                for c in companies
            ]
            return responses, total
