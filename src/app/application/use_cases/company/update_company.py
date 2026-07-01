"""Caso de uso para update company."""

from app.application.dtos.company_dtos import CompanyResponse, UpdateCompanyRequest
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.enums import CompanyStatus
from app.domain.exceptions import CompanyNotFoundError, StaleDataError, ValidationException
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

            if request.version is not None and request.version != company.version:
                raise StaleDataError(
                    f"Conflicto de versión para empresa: se esperaba {request.version}, "
                    f"la actual es {company.version}."
                )

            if "nombre" in request._fields_set:
                if request.nombre is None or not request.nombre.strip():
                    raise ValidationException("El nombre de la empresa no puede estar vacío.")
                company.rename(request.nombre)

            if "rif" in request._fields_set or "email_contacto" in request._fields_set:
                rif = request.rif if "rif" in request._fields_set else company.rif
                email_contacto = (
                    request.email_contacto
                    if "email_contacto" in request._fields_set
                    else company.email_contacto
                )
                company.update_profile(rif=rif, email_contacto=email_contacto)

            if "estado" in request._fields_set:
                if request.estado is None:
                    raise ValidationException("El estado no puede ser nulo.")
                target = CompanyStatus(request.estado)
                if target != company.estado:
                    if target == CompanyStatus.SUSPENDED:
                        company.suspend()
                    elif target == CompanyStatus.ACTIVE:
                        company.activate()
                    elif target == CompanyStatus.CANCELLED:
                        company.cancel()
                    else:
                        raise ValidationException(
                            f"Transición de '{company.estado.value}' a "
                            f"'{target.value}' no permitida."
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
