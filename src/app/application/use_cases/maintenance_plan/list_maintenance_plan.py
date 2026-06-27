"""Caso de uso: Listar planes de mantenimiento."""

from collections.abc import Sequence

from app.application.dtos.maintenance_plan_dtos import MaintenancePlanResponse
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.value_objects import CompanyId


class ListMaintenancePlansUseCase:
    """Caso de uso para listar planes de mantenimiento con paginación y filtros."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(
        self,
        company_id_str: str,
        offset: int = 0,
        limit: int = 20,
        filters: dict[str, object] | None = None,
    ) -> tuple[Sequence[MaintenancePlanResponse], int]:
        """Lista los planes de mantenimiento.

        Args:
            company_id_str (str): UUID de la empresa.
            offset (int): Número de registros a saltar.
            limit (int): Máximo de registros por página.
            filters (dict[str, object] | None): Filtros opcionales (activo_id, tipo, activo).

        Returns:
            tuple[Sequence[MaintenancePlanResponse], int]: Lista de respuestas y total de registros.
        """
        company_id = CompanyId.from_string(company_id_str)

        async with self.uow:
            plans, total = await self.uow.maintenance_plans.get_all_by_company(
                company_id, offset, limit, filters or {},
            )

            result = [
                MaintenancePlanResponse(
                    id=str(p.id),
                    empresa_id=str(p.empresa_id),
                    activo_id=str(p.activo_id),
                    nombre=p.nombre,
                    tipo=p.tipo.value,
                    intervalo_dias=p.intervalo_dias,
                    proxima_ejecucion=p.proxima_ejecucion,
                    tecnico_responsable_id=(
                        str(p.tecnico_responsable_id) if p.tecnico_responsable_id else None
                    ),
                    descripcion_tareas=p.descripcion_tareas,
                    activo=p.activo,
                    created_at=p.created_at,
                    updated_at=p.updated_at,
                )
                for p in plans
            ]

        return result, total
