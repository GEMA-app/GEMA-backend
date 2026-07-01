"""Puerto de repositorio para PlanExecution."""

from typing import Protocol
from uuid import UUID

from app.domain.entities.plan_execution import PlanExecution
from app.domain.value_objects import CompanyId, PlanExecutionId


class PlanExecutionRepositoryPort(Protocol):
    """Puerto para el repositorio de ejecuciones de plan."""

    async def get_by_id(self, id: PlanExecutionId, empresa_id: CompanyId) -> PlanExecution | None:
        """Obtiene una ejecución por su ID y empresa.

        Args:
            id: ID de la ejecución.
            empresa_id: ID de la empresa.

        Returns:
            La ejecución si existe, None si no.
        """
        ...

    async def list_by_plan_id(self, plan_id: UUID, empresa_id: CompanyId) -> list[PlanExecution]:
        """Lista todas las ejecuciones de un plan en una empresa.

        Args:
            plan_id: ID del plan de mantenimiento.
            empresa_id: ID de la empresa.

        Returns:
            Lista de ejecuciones.
        """
        ...

    async def save(self, execution: PlanExecution) -> PlanExecution:
        """Persiste una ejecución de plan.

        Args:
            execution: Entidad PlanExecution a persistir.

        Returns:
            La entidad persistida con sus IDs generados.
        """
        ...
