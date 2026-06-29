"""Caso de uso para eliminar una intervención técnica."""

from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.exceptions.intervention import InterventionNotFoundError
from app.domain.value_objects.identifier import CompanyId, InterventionId


class DeleteInterventionUseCase:
    """Caso de uso para eliminar una intervención técnica."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self._uow = uow

    async def execute(self, ot_id: str, intervention_id: str, empresa_id: str) -> None:
        """Elimina una intervención técnica por su ID.

        Args:
            ot_id: Identificador UUID de la orden de trabajo (desde el path).
            intervention_id: Identificador UUID de la intervención.
            empresa_id: Identificador UUID de la empresa.

        Raises:
            InterventionNotFoundError: Si no existe la intervención con el ID.
        """
        intervention_id_internal = InterventionId.from_string(intervention_id)
        company_id = CompanyId.from_string(empresa_id)

        async with self._uow:
            intervention = await self._uow.interventions.get_by_id(
                intervention_id_internal, company_id
            )
            if intervention is None:
                raise InterventionNotFoundError(f"Intervención {intervention_id} no encontrada")

            await self._uow.interventions.delete(intervention_id_internal, company_id)
            await self._uow.commit()
