"""Caso de uso para validar una orden de trabajo."""

from app.application.dtos.work_order_dtos import WorkOrderResponse
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.exceptions import WorkOrderNotFoundError
from app.domain.value_objects import CompanyId, UserId, WorkOrderId


class ValidateWorkOrderUseCase:
    """Caso de uso para validar una orden de trabajo."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(
        self, company_id: str, work_order_id: str, validator_id: str
    ) -> WorkOrderResponse:
        """Valida una orden de trabajo cerrando la misma de forma definitiva.

        Args:
            company_id: Identificador de la empresa.
            work_order_id: Identificador de la orden de trabajo.
            validator_id: Identificador del usuario que valida (supervisor/admin).
        """
        company = CompanyId.from_string(company_id)
        wo_id = WorkOrderId.from_string(work_order_id)
        validator = UserId.from_string(validator_id)

        async with self.uow:
            wo = await self.uow.work_orders.get_by_id(wo_id, company)
            if not wo:
                raise WorkOrderNotFoundError(
                    f"Orden de trabajo con ID '{work_order_id}' no encontrada."
                )

            wo.validate(validator)
            await self.uow.work_orders.save(wo)
            await self.uow.commit()

        return WorkOrderResponse.from_entity(wo)
