"""Puerto para el repositorio de MaintenancePlan."""

from collections.abc import Sequence
from typing import Protocol

from app.domain.entities.maintenance_plan import MaintenancePlan
from app.domain.value_objects import CompanyId, MaintenancePlanId


class MaintenancePlanRepositoryPort(Protocol):
    """Interfaz para la persistencia de planes de mantenimiento."""

    async def get_by_id(
        self, plan_id: MaintenancePlanId, company_id: CompanyId
    ) -> MaintenancePlan | None:
        """Obtiene un plan por su ID, validando el tenant.

        Args:
            plan_id: Identificador del plan.
            company_id: Identificador de la empresa.

        Returns:
            El plan si existe, None en caso contrario.
        """
        ...

    async def get_all_by_company(
        self,
        company_id: CompanyId,
        offset: int = 0,
        limit: int = 20,
        filters: dict[str, object] | None = None,
    ) -> tuple[Sequence[MaintenancePlan], int]:
        """Lista los planes de mantenimiento de una empresa con paginación.

        Args:
            company_id: Identificador de la empresa.
            offset: Número de registros a saltar.
            limit: Máximo de registros por página.
            filters: Filtros opcionales (activo_id, tipo, activo, etc.).

        Returns:
            Tupla con la lista de planes y el total de registros.
        """
        ...

    async def save(self, plan: MaintenancePlan) -> MaintenancePlan:
        """Persiste un nuevo plan de mantenimiento.

        Args:
            plan: Entidad del plan a crear.

        Returns:
            El plan persistido con su ID generado.
        """
        ...

    async def update(self, plan: MaintenancePlan) -> MaintenancePlan:
        """Actualiza un plan de mantenimiento existente.

        Args:
            plan: Entidad del plan con los datos actualizados.

        Returns:
            El plan actualizado.
        """
        ...

    async def delete(self, plan_id: MaintenancePlanId, company_id: CompanyId) -> None:
        """Elimina un plan de mantenimiento por su ID.

        Args:
            plan_id: Identificador del plan.
            company_id: Identificador de la empresa.
        """
        ...
