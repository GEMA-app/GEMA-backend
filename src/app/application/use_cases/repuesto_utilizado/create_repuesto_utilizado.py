from uuid import UUID

from app.application.dtos.repuesto_utilizado_dtos import (
    CreateRepuestoUtilizadoRequest,
    RepuestoUtilizadoResponse,
)
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.entities.repuesto_utilizado import RepuestoUtilizado
from app.domain.value_objects import UserId


class CreateRepuestoUtilizadoUseCase:
    """Caso de uso para registrar un nuevo repuesto utilizado."""

    def __init__(self, uow: UnitOfWorkPort):
        self.uow = uow

    async def execute(
        self, company_id_str: str, request: CreateRepuestoUtilizadoRequest
    ) -> RepuestoUtilizadoResponse:
        # Usar UserId para el company_id
        company_id = UserId.from_string(company_id_str)
        
        # Usar UUID directamente para los otros IDs
        intervencion_id = request.intervencion_id
        repuesto_id = request.repuesto_id

        nuevo_repuesto = RepuestoUtilizado.create(
            empresa_id=company_id,
            intervencion_id=intervencion_id,
            repuesto_id=repuesto_id,
            cantidad_usada=request.cantidad_usada,
            precio_unitario=request.precio_unitario,
            moneda=request.moneda,
        )

        async with self.uow:
            await self.uow.repuestos_utilizados.save(nuevo_repuesto)
            await self.uow.commit()

        return RepuestoUtilizadoResponse(
            id=nuevo_repuesto.id,
            empresa_id=nuevo_repuesto.empresa_id.value,
            intervencion_id=nuevo_repuesto.intervencion_id,
            repuesto_id=nuevo_repuesto.repuesto_id,
            cantidad_usada=nuevo_repuesto.cantidad_usada,
            precio_unitario=nuevo_repuesto.precio_unitario,
            moneda=nuevo_repuesto.moneda,
            created_at=nuevo_repuesto.created_at,
            updated_at=nuevo_repuesto.updated_at,
        )