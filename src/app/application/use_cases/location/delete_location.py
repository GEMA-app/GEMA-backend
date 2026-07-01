"""Caso de uso para delete location."""
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.exceptions import LocationNotFoundError
from app.domain.value_objects import CompanyId, LocationId


class DeleteLocationUseCase:
    """Caso de uso para eliminar una ubicación."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(self, company_id_str: str, location_id_str: str) -> None:
        """Elimina una ubicación por su ID."""
        company_id = CompanyId.from_string(company_id_str)
        location_id = LocationId.from_string(location_id_str)

        async with self.uow:
            location = await self.uow.locations.get_by_id(location_id, company_id)
            if not location:
                raise LocationNotFoundError(
                    f"La ubicación con ID '{location_id_str}' no existe en esta empresa."
                )

            await self.uow.locations.delete(location_id, company_id)
            await self.uow.commit()
