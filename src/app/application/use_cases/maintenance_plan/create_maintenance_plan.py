"""Caso de uso: Crear un plan de mantenimiento."""

from app.application.dtos.maintenance_plan_dtos import (
    CreateMaintenancePlanRequest,
    MaintenancePlanResponse,
)
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.entities.maintenance_plan import MaintenancePlan
from app.domain.enums import MaintenanceType
from app.domain.value_objects import AssetId, CompanyId, UserId


class CreateMaintenancePlanUseCase:
    """Caso de uso para crear un nuevo plan de mantenimiento."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(
        self, company_id_str: str, request: CreateMaintenancePlanRequest
    ) -> MaintenancePlanResponse:
        """Crea un plan de mantenimiento y lo persiste.

        Args:
            company_id_str (str): UUID de la empresa.
            request (CreateMaintenancePlanRequest): DTO con los datos del plan.

        Returns:
            MaintenancePlanResponse: Con los datos del plan creado.
        """
        company_id = CompanyId.from_string(company_id_str)
        activo_id = AssetId.from_string(request.activo_id)

        tecnico_id: UserId | None = None
        if request.tecnico_responsable_id:
            tecnico_id = UserId.from_string(request.tecnico_responsable_id)

        plan = MaintenancePlan.create(
            empresa_id=company_id,
            activo_id=activo_id,
            nombre=request.nombre,
            tipo=MaintenanceType(request.tipo),
            intervalo_dias=request.intervalo_dias,
            proxima_ejecucion=request.proxima_ejecucion,
            tecnico_responsable_id=tecnico_id,
            descripcion_tareas=request.descripcion_tareas,
        )

        async with self.uow:
            saved = await self.uow.maintenance_plans.save(plan)
            await self.uow.commit()

        return MaintenancePlanResponse(
            id=str(saved.id),
            empresa_id=str(saved.empresa_id),
            activo_id=str(saved.activo_id),
            nombre=saved.nombre,
            tipo=saved.tipo.value,
            intervalo_dias=saved.intervalo_dias,
            proxima_ejecucion=saved.proxima_ejecucion,
            tecnico_responsable_id=(
                str(saved.tecnico_responsable_id) if saved.tecnico_responsable_id else None
            ),
            descripcion_tareas=saved.descripcion_tareas,
            activo=saved.activo,
            created_at=saved.created_at,
            updated_at=saved.updated_at,
        )
