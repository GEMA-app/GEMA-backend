from app.application.dtos.company_dtos import CompanyResponse, UpdateCompanyRequest
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.enums import CompanyStatus
from app.domain.exceptions import CompanyNotFoundError, ValidationException
from app.domain.value_objects import CompanyId


class UpdateCompanyUseCase:
    """Actualiza los datos de una empresa."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        """Guarda dependencias."""
        self.uow = uow

    async def execute(self, company_id_str: str, request: UpdateCompanyRequest) -> CompanyResponse:
        """Actualiza la información de la empresa."""
        company_id = CompanyId.from_string(company_id_str)
        async with self.uow:
            company = await self.uow.companies.get_by_id(company_id)
            if not company:
                raise CompanyNotFoundError(f"La empresa con ID '{company_id_str}' no existe.")

            if request.nombre is not None:
                if not request.nombre.strip():
                    raise ValidationException("El nombre de la empresa no puede estar vacío.")
                company.nombre = request.nombre.strip()

            if request.rif is not None:
                company.rif = request.rif

            if request.email_contacto is not None:
                company.email_contacto = request.email_contacto

            if request.estado is not None:
                company.estado = CompanyStatus(request.estado)

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
            )
