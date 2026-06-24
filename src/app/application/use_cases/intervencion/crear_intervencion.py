"""Caso de uso para crear una intervención técnica."""

from datetime import datetime

from app.application.dtos.intervencion_dtos import CrearIntervencionRequest, IntervencionResponse
from app.application.ports.intervencion_repository import IntervencionRepositoryPort
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.entities.intervencion_tecnica import IntervencionTecnica
from app.domain.exceptions.intervencion import IntervencionInvalidDataError
from app.domain.value_objects.identifier import OrdenTrabajoId, UserId


class CrearIntervencionUseCase:
    """Caso de uso para crear una nueva intervención técnica."""

    def __init__(
        self,
        uow: UnitOfWorkPort,
        intervencion_repository: IntervencionRepositoryPort,
    ) -> None:
        self._uow = uow
        self._intervencion_repository = intervencion_repository

    async def execute(self, request: CrearIntervencionRequest) -> IntervencionResponse:
        """Ejecuta el caso de uso."""
        # Validar fechas
        if request.fecha_inicio > datetime.now():
            raise IntervencionInvalidDataError("La fecha de inicio no puede ser futura")

        if request.horas_trabajadas < 0:
            raise IntervencionInvalidDataError("Las horas trabajadas no pueden ser negativas")

        if request.costo < 0:
            raise IntervencionInvalidDataError("El costo no puede ser negativo")

        # Crear la entidad
        intervencion = IntervencionTecnica.crear(
            orden_trabajo_id=OrdenTrabajoId.from_string(str(request.orden_trabajo_id)),
            tecnico_id=UserId.from_string(str(request.tecnico_id)),
            descripcion=request.descripcion,
            fecha_inicio=request.fecha_inicio,
            horas_trabajadas=request.horas_trabajadas,
            costo=request.costo,
            observaciones=request.observaciones,
        )

        # Persistir
        async with self._uow:
            await self._intervencion_repository.save(intervencion)
            await self._uow.commit()

        # Devolver respuesta
        return IntervencionResponse(
            id=intervencion.id.value,
            orden_trabajo_id=intervencion.orden_trabajo_id.value,
            tecnico_id=intervencion.tecnico_id.value,
            descripcion=intervencion.descripcion,
            fecha_inicio=intervencion.fecha_inicio,
            fecha_fin=intervencion.fecha_fin,
            horas_trabajadas=intervencion.horas_trabajadas,
            costo=intervencion.costo,
            estado=intervencion.estado,
            observaciones=intervencion.observaciones,
        )