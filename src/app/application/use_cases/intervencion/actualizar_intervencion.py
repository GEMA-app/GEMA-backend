"""Caso de uso para actualizar una intervención técnica."""

from app.application.dtos.intervencion_dtos import (
    ActualizarIntervencionRequest,
    IntervencionResponse,
)
from app.application.ports.intervencion_repository import IntervencionRepositoryPort
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.exceptions.intervencion import (
    IntervencionInvalidDataError,
    IntervencionNotFoundError,
)
from app.domain.value_objects.identifier import CompanyId, IntervencionId


class ActualizarIntervencionUseCase:
    """Caso de uso para actualizar una intervención técnica existente."""

    def __init__(
        self,
        uow: UnitOfWorkPort,
        intervencion_repository: IntervencionRepositoryPort,
    ) -> None:
        self._uow = uow
        self._intervencion_repository = intervencion_repository

    async def execute(
        self, intervencion_id: str, empresa_id: str, request: ActualizarIntervencionRequest
    ) -> IntervencionResponse:
        """Ejecuta el caso de uso."""
        interv_id = IntervencionId.from_string(intervencion_id)
        company_id = CompanyId.from_string(empresa_id)

        async with self._uow:
            intervencion = await self._intervencion_repository.get_by_id(interv_id, company_id)

            if intervencion is None:
                raise IntervencionNotFoundError(f"Intervención {intervencion_id} no encontrada")

            # Validar datos (si se proporcionan)
            if request.horas_trabajadas is not None and request.horas_trabajadas < 0:
                raise IntervencionInvalidDataError("Las horas trabajadas no pueden ser negativas")

            if request.costo is not None and request.costo < 0:
                raise IntervencionInvalidDataError("El costo no puede ser negativo")

            # Actualizar (como es frozen, necesitamos recrear la entidad)
            from dataclasses import replace

            nueva_intervencion = replace(
                intervencion,
                descripcion=request.descripcion or intervencion.descripcion,
                horas_trabajadas=request.horas_trabajadas or intervencion.horas_trabajadas,
                costo=request.costo or intervencion.costo,
                observaciones=request.observaciones if request.observaciones is not None else intervencion.observaciones,
            )

            await self._intervencion_repository.save(nueva_intervencion)
            await self._uow.commit()

            return IntervencionResponse(
                id=nueva_intervencion.id.value,
                orden_trabajo_id=nueva_intervencion.orden_trabajo_id.value,
                tecnico_id=nueva_intervencion.tecnico_id.value,
                descripcion=nueva_intervencion.descripcion,
                fecha_inicio=nueva_intervencion.fecha_inicio,
                fecha_fin=nueva_intervencion.fecha_fin,
                horas_trabajadas=nueva_intervencion.horas_trabajadas,
                costo=nueva_intervencion.costo,
                estado=nueva_intervencion.estado,
                observaciones=nueva_intervencion.observaciones,
            )