"""Caso de uso para crear una nueva orden de trabajo."""

import uuid

from app.application.dtos.work_order_dtos import (
    CreateWorkOrderRequest,
    WorkOrderResponse,
)
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.entities import WorkOrder
from app.domain.enums import MaintenanceType
from app.domain.exceptions import AssetNotFoundError, WorkOrderCodeExistsError
from app.domain.value_objects import AssetId, CompanyId, UserId, WorkOrderId


class CreateWorkOrderUseCase:
    """Caso de uso para crear una nueva orden de trabajo.

    Valida que el activo exista, que el código (si se proporciona) no esté
    duplicado en la empresa, y persiste la orden con estado inicial OPEN.
    """

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(
        self, company_id: str, request: CreateWorkOrderRequest
    ) -> WorkOrderResponse:
        """Ejecuta la creación de una orden de trabajo.

        Args:
            company_id: Identificador de la empresa.
            request: DTO con los datos de la orden a crear.

        Returns:
            WorkOrderResponse: DTO con los datos de la orden creada.

        Raises:
            AssetNotFoundError: Si el activo especificado no existe.
            WorkOrderCodeExistsError: Si el código ya está registrado.
        """
        company = CompanyId.from_string(company_id)
        activo_id = AssetId.from_string(request.activo_id)

        async with self.uow:
            asset = await self.uow.assets.get_by_id(activo_id, company)
            if not asset:
                raise AssetNotFoundError(
                    f"Activo con ID '{request.activo_id}' no encontrado."
                )

            codigo_ot = request.codigo_ot or WorkOrder.generate_code(company)

            existing = await self.uow.work_orders.get_by_code(codigo_ot, company)
            if existing:
                raise WorkOrderCodeExistsError(
                    f"Ya existe una orden de trabajo con código '{codigo_ot}' en esta empresa."
                )

            work_order = WorkOrder.create(
                work_order_id=WorkOrderId(uuid.uuid4()),
                empresa_id=company,
                codigo_ot=codigo_ot,
                activo_id=activo_id,
                tipo=MaintenanceType(request.tipo),
                supervisor_id=(
                    UserId.from_string(request.supervisor_id)
                    if request.supervisor_id
                    else None
                ),
                descripcion_trabajo=request.descripcion_trabajo,
                costo_estimado=request.costo_estimado,
                moneda=request.moneda,
            )

            await self.uow.work_orders.save(work_order)
            await self.uow.commit()

        return WorkOrderResponse.from_entity(work_order)
