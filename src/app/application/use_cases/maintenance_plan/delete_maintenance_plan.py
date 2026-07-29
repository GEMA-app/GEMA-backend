"""Caso de uso: Eliminar un plan de mantenimiento."""

from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.events import MaintenancePlanDeleted
from app.domain.exceptions.maintenance_plan import MaintenancePlanNotFoundError
from app.domain.value_objects import CompanyId, MaintenancePlanId


class DeleteMaintenancePlanUseCase:
    """Caso de uso para eliminar un plan de mantenimiento."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(self, company_id_str: str, plan_id_str: str) -> None:
        """Elimina un plan de mantenimiento por ID.

        Args:
            company_id_str (str): UUID de la empresa.
            plan_id_str (str): UUID del plan a eliminar.

        Raises:
            MaintenancePlanNotFoundError: Si el plan no existe en la empresa.
        """
        company_id = CompanyId.from_string(company_id_str)
        plan_id = MaintenancePlanId.from_string(plan_id_str)

        async with self.uow:
            plan = await self.uow.maintenance_plans.get_by_id(plan_id, company_id)
            if not plan:
                raise MaintenancePlanNotFoundError(plan_id_str, company_id_str)
            await self.uow.maintenance_plans.delete(plan_id, company_id)

            self.uow.add_event(
                MaintenancePlanDeleted(
                    maintenance_plan_id=plan_id_str,
                    empresa_id=str(company_id),
                )
            )
            await self.uow.commit()
