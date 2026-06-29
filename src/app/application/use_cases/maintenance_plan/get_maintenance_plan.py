"""Caso de uso: Obtener un plan de mantenimiento por ID."""

from datetime import date

from app.application.dtos.maintenance_plan_dtos import MaintenancePlanResponse
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.exceptions.maintenance_plan import MaintenancePlanNotFoundError
from app.domain.value_objects import CompanyId, MaintenancePlanId


class GetMaintenancePlanUseCase:
    """Caso de uso para obtener el detalle de un plan de mantenimiento."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(self, company_id_str: str, plan_id_str: str) -> MaintenancePlanResponse:
        """Obtiene un plan por ID.

        Args:
            company_id_str (str): UUID de la empresa.
            plan_id_str (str): UUID del plan.

        Returns:
            MaintenancePlanResponse: Con los datos del plan.

        Raises:
            MaintenancePlanNotFoundError: Si el plan no existe en la empresa.
        """
        company_id = CompanyId.from_string(company_id_str)
        plan_id = MaintenancePlanId.from_string(plan_id_str)

        async with self.uow:
            plan = await self.uow.maintenance_plans.get_by_id(plan_id, company_id)

            if not plan:
                raise MaintenancePlanNotFoundError(plan_id_str, company_id_str)

            return MaintenancePlanResponse(
                id=str(plan.id),
                empresa_id=str(plan.empresa_id),
                activo_id=str(plan.activo_id),
                nombre=plan.nombre,
                tipo=plan.tipo.value,
                intervalo_dias=plan.intervalo_dias,
                proxima_ejecucion=plan.proxima_ejecucion,
                tecnico_responsable_id=(
                    str(plan.tecnico_responsable_id) if plan.tecnico_responsable_id else None
                ),
                descripcion_tareas=plan.descripcion_tareas,
                activo=plan.activo,
                created_at=plan.created_at,
                updated_at=plan.updated_at,
                es_urgente=(plan.proxima_ejecucion - date.today()).days <= 7,
            )
