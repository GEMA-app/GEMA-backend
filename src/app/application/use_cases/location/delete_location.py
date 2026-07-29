"""Caso de uso para delete location."""

from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.events import LocationDeleted
from app.domain.exceptions import LocationNotFoundError
from app.domain.value_objects import CompanyId, LocationId


class DeleteLocationUseCase:
    """Caso de uso para eliminar una ubicación con eliminación en cascada."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def _delete_cascade(self, location_id: LocationId, company_id: CompanyId) -> None:
        """Elimina recursivamente una ubicación y todas sus sububicaciones hijas."""
        children = await self.uow.locations.get_children(location_id, company_id)
        for child in children:
            await self._delete_cascade(child.id, company_id)
        await self.uow.locations.delete(location_id, company_id)
        self.uow.add_event(
            LocationDeleted(
                location_id=str(location_id),
                nombre="",
                empresa_id=str(company_id),
            )
        )

    async def execute(self, company_id_str: str, location_id_str: str) -> None:
        """Elimina una ubicación y todas sus sububicaciones en cascada por su ID."""
        company_id = CompanyId.from_string(company_id_str)
        location_id = LocationId.from_string(location_id_str)

        async with self.uow:
            location = await self.uow.locations.get_by_id(location_id, company_id)
            if not location:
                raise LocationNotFoundError(
                    f"La ubicación con ID '{location_id_str}' no existe en esta empresa."
                )

            await self._delete_cascade(location_id, company_id)
            await self.uow.commit()
