"""Caso de uso para obtener una intervención técnica por ID."""

from app.application.dtos.intervention_dtos import InterventionResponse
from app.application.dtos.used_part_dtos import UsedPartResponse
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.exceptions.intervention import InterventionNotFoundError
from app.domain.value_objects.identifier import CompanyId, InterventionId


class GetInterventionUseCase:
    """Caso de uso para obtener una intervención técnica por ID."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self._uow = uow

    async def execute(
        self, empresa_id: str, ot_id: str, intervention_id: str
    ) -> InterventionResponse:
        """Ejecuta el caso de uso para obtener una intervención por ID.

        Args:
            empresa_id: Identificador UUID de la empresa.
            ot_id: Identificador UUID de la orden de trabajo (desde el path).
            intervention_id: Identificador UUID de la intervención.

        Returns:
            InterventionResponse con los datos de la intervención encontrada.

        Raises:
            InterventionNotFoundError: Si no existe la intervención con el ID
                proporcionado en la empresa especificada.
        """
        intervention_id_internal = InterventionId.from_string(intervention_id)
        company_id = CompanyId.from_string(empresa_id)

        async with self._uow:
            intervention = await self._uow.interventions.get_by_id(
                intervention_id_internal, company_id
            )

            if intervention is None:
                raise InterventionNotFoundError(f"Intervención {intervention_id} no encontrada")

            used_parts = await self._uow.used_parts.get_by_intervention(
                company_id, intervention_id_internal
            )

        return InterventionResponse(
            id=intervention.id.value,
            empresa_id=intervention.empresa_id.value,
            work_order_id=intervention.work_order_id.value,
            technician_id=intervention.technician_id.value,
            tareas_realizadas=intervention.tareas_realizadas,
            fecha_inicio=intervention.fecha_inicio,
            fecha_fin=intervention.fecha_fin,
            horas_hombre=intervention.horas_hombre,
            used_parts=[
                UsedPartResponse(
                    id=p.id,
                    empresa_id=p.empresa_id.value,
                    intervencion_id=p.intervencion_id,
                    repuesto_id=p.repuesto_id,
                    cantidad_usada=p.cantidad_usada,
                    precio_unitario=p.precio_unitario,
                    moneda=p.moneda,
                    created_at=p.created_at,
                    updated_at=p.updated_at,
                    precio_total=(
                        p.cantidad_usada * p.precio_unitario
                        if p.precio_unitario is not None
                        else None
                    ),
                )
                for p in used_parts
            ],
        )
