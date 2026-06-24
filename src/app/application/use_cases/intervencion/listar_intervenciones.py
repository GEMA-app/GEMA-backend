"""Caso de uso para listar intervenciones técnicas."""

from app.application.dtos.intervencion_dtos import IntervencionResponse
from app.application.ports.intervencion_repository import IntervencionRepositoryPort
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.value_objects.identifier import CompanyId


class ListarIntervencionesUseCase:
    """Caso de uso para listar intervenciones técnicas de una empresa."""

    def __init__(
        self,
        uow: UnitOfWorkPort,
        intervencion_repository: IntervencionRepositoryPort,
    ) -> None:
        self._uow = uow
        self._intervencion_repository = intervencion_repository

    async def execute(
        self, empresa_id: str, offset: int = 0, limit: int = 100
    ) -> tuple[list[IntervencionResponse], int]:
        """Ejecuta el caso de uso."""
        company_id = CompanyId.from_string(empresa_id)

        async with self._uow:
            intervenciones, total = await self._intervencion_repository.list(
                empresa_id=company_id,
                offset=offset,
                limit=limit,
            )

        return [
            IntervencionResponse(
                id=i.id.value,
                orden_trabajo_id=i.orden_trabajo_id.value,
                tecnico_id=i.tecnico_id.value,
                descripcion=i.descripcion,
                fecha_inicio=i.fecha_inicio,
                fecha_fin=i.fecha_fin,
                horas_trabajadas=i.horas_trabajadas,
                costo=i.costo,
                estado=i.estado,
                observaciones=i.observaciones,
            )
            for i in intervenciones
        ], total