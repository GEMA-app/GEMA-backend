"""Caso de uso: Actualizar un plan de mantenimiento."""

from datetime import date

from app.application.dtos.maintenance_plan_dtos import (
    MaintenancePlanResponse,
    UpdateMaintenancePlanRequest,
)
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.enums import MaintenanceType
from app.domain.events import MaintenancePlanUpdated
from app.domain.exceptions.maintenance_plan import (
    MaintenancePlanIntervalError,
    MaintenancePlanNotFoundError,
)
from app.domain.value_objects import CompanyId, MaintenancePlanId, UserId


class UpdateMaintenancePlanUseCase:
    """Caso de uso para actualizar un plan de mantenimiento existente."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(
        self, company_id_str: str, plan_id_str: str, request: UpdateMaintenancePlanRequest
    ) -> MaintenancePlanResponse:
        """Actualiza los datos de un plan de mantenimiento.

        Args:
            company_id_str (str): UUID de la empresa.
            plan_id_str (str): UUID del plan.
            request (UpdateMaintenancePlanRequest): DTO con los campos a actualizar.

        Returns:
            MaintenancePlanResponse: Con los datos actualizados.

        Raises:
            MaintenancePlanNotFoundError: Si el plan no existe.
        """
        company_id = CompanyId.from_string(company_id_str)
        plan_id = MaintenancePlanId.from_string(plan_id_str)

        async with self.uow:
            plan = await self.uow.maintenance_plans.get_by_id(plan_id, company_id)
            if not plan:
                raise MaintenancePlanNotFoundError(plan_id_str, company_id_str)

            # Partial update: solo aplica campos presentes en _fields_set
            if "nombre" in request._fields_set and request.nombre is not None:
                plan.nombre = request.nombre
            if "tipo" in request._fields_set and request.tipo is not None:
                plan.tipo = MaintenanceType(request.tipo)
            if "intervalo_dias" in request._fields_set and request.intervalo_dias is not None:
                if request.intervalo_dias <= 0:
                    raise MaintenancePlanIntervalError(request.intervalo_dias)
                plan.intervalo_dias = request.intervalo_dias
            if "proxima_ejecucion" in request._fields_set and request.proxima_ejecucion is not None:
                plan.proxima_ejecucion = request.proxima_ejecucion
            # tecnico_id acepta None explícito para desasignar el técnico
            if "tecnico_responsable_id" in request._fields_set:
                tid = request.tecnico_responsable_id
                plan.tecnico_responsable_id = UserId.from_string(tid) if tid else None
            if "descripcion_tareas" in request._fields_set:
                plan.descripcion_tareas = request.descripcion_tareas
            # activo usa métodos de la entidad para mantener encapsulación
            if "activo" in request._fields_set and request.activo is not None:
                if request.activo:
                    plan.activate()
                else:
                    plan.deactivate()

            updated = await self.uow.maintenance_plans.update(plan)

            self.uow.add_event(
                MaintenancePlanUpdated(
                    maintenance_plan_id=str(updated.id),
                    empresa_id=str(company_id),
                )
            )
            await self.uow.commit()

        return MaintenancePlanResponse(
            id=str(updated.id),
            empresa_id=str(updated.empresa_id),
            activo_id=str(updated.activo_id),
            nombre=updated.nombre,
            tipo=updated.tipo.value,
            intervalo_dias=updated.intervalo_dias,
            proxima_ejecucion=updated.proxima_ejecucion,
            tecnico_responsable_id=(
                str(updated.tecnico_responsable_id) if updated.tecnico_responsable_id else None
            ),
            descripcion_tareas=updated.descripcion_tareas,
            activo=updated.activo,
            created_at=updated.created_at,
            updated_at=updated.updated_at,
            es_urgente=(updated.proxima_ejecucion - date.today()).days <= 7,
        )
