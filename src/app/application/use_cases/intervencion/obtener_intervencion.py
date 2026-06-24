"""Caso de uso para obtener una intervención técnica por ID."""

from app.application.dtos.intervencion_dtos import IntervencionResponse
from app.application.ports.intervencion_repository import IntervencionRepositoryPort
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.exceptions.intervencion import IntervencionNotFoundError
from app.domain.value_objects.identifier import CompanyId, IntervencionId


class ObtenerIntervencionUseCase:
    """Caso de uso para obtener una intervención técnica por ID."""

    def __init__(
        self,
        uow: UnitOfWorkPort,
        intervencion_repository: IntervencionRepositoryPort,
    ) -> None:
        self._uow = uow
        self._intervencion_repository = intervencion_repository

    async def execute(self, intervencion_id: str, empresa_id: str) -> IntervencionResponse:
        """Ejecuta el caso de uso."""
        interv_id = IntervencionId.from_string(intervencion_id)
        company_id = CompanyId.from_string(empresa_id)

        async with self._uow:
            intervencion = await self._intervencion_repository.get_by_id(interv_id, company_id)

        if intervencion is None:
            raise IntervencionNotFoundError(f"Intervención {intervencion_id} no encontrada")

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