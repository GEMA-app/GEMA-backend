"""Caso de uso para delete company."""
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.exceptions import CompanyNotFoundError
from app.domain.value_objects import CompanyId


class DeleteCompanyUseCase:
    """Caso de uso para eliminar una empresa."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(self, company_id_str: str) -> None:
        """Elimina una empresa por su ID."""
        company_id = CompanyId.from_string(company_id_str)
        async with self.uow:
            company = await self.uow.companies.get_by_id(company_id)
            if not company:
                raise CompanyNotFoundError(f"La empresa con ID '{company_id_str}' no existe.")

            await self.uow.companies.delete(company_id)
            await self.uow.commit()
