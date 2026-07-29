"""Caso de uso para listar intervenciones técnicas."""

from app.application.dtos.intervention_dtos import InterventionResponse
from app.application.dtos.used_part_dtos import UsedPartResponse
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.value_objects.identifier import CompanyId, InterventionId, UserId, WorkOrderId


class ListInterventionsUseCase:
    """Caso de uso para listar intervenciones técnicas de una orden de trabajo."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self._uow = uow

    async def execute(
        self,
        empresa_id: str,
        ot_id: str,
        offset: int = 0,
        limit: int = 100,
        tecnico_id: str | None = None,
    ) -> tuple[list[InterventionResponse], int]:
        """Ejecuta el caso de uso para listar intervenciones de una orden de trabajo.

        Args:
            empresa_id: Identificador UUID de la empresa.
            ot_id: Identificador UUID de la orden de trabajo.
            offset: Número de registros a omitir (paginación).
            limit: Cantidad máxima de registros a retornar.
            tecnico_id: Filtrar por ID del técnico asignado.

        Returns:
            Una tupla con la lista de InterventionResponse y el total de registros.
        """
        company_id = CompanyId.from_string(empresa_id)
        work_order_id = WorkOrderId.from_string(ot_id)

        async with self._uow:
            interventions = await self._uow.interventions.get_by_work_order(
                work_order_id=work_order_id,
                empresa_id=company_id,
            )

            if tecnico_id:
                tech_id = UserId.from_string(tecnico_id)
                interventions = [i for i in interventions if i.technician_id == tech_id]

            # ponytail: N+1 query — acceptable for typical intervention counts (<50).
            # Optimize with JOIN if pagination exceeds 50.
            used_parts_map: dict[str, list[UsedPartResponse]] = {}
            for i in interventions:
                parts = await self._uow.used_parts.get_by_intervention(
                    company_id, InterventionId(i.id.value)
                )
                used_parts_map[str(i.id.value)] = [
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
                    for p in parts
                ]

        return [
            InterventionResponse(
                id=i.id.value,
                empresa_id=i.empresa_id.value,
                work_order_id=i.work_order_id.value,
                technician_id=i.technician_id.value,
                tareas_realizadas=i.tareas_realizadas,
                fecha_inicio=i.fecha_inicio,
                fecha_fin=i.fecha_fin,
                horas_hombre=i.horas_hombre,
                used_parts=used_parts_map.get(str(i.id.value), []),
            )
            for i in interventions
        ], len(interventions)
