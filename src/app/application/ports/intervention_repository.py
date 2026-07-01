"""Puerto para el repositorio de intervenciones técnicas."""

from typing import Protocol

from app.domain.entities.intervention import TechnicalIntervention
from app.domain.value_objects.identifier import CompanyId, InterventionId, UserId, WorkOrderId


class InterventionRepositoryPort(Protocol):
    """Contrato para el repositorio de intervenciones técnicas."""

    async def save(self, intervention: TechnicalIntervention) -> None:
        """Persiste una intervención técnica en la base de datos.

        Args:
            intervention: Entidad de dominio a persistir.
        """
        ...

    async def get_by_id(
        self, id: InterventionId, empresa_id: CompanyId
    ) -> TechnicalIntervention | None:
        """Obtiene una intervención por su ID y empresa.

        Args:
            id: Identificador único de la intervención.
            empresa_id: Identificador de la empresa (tenant).

        Returns:
            La entidad TechnicalIntervention si existe, o None si no fue encontrada.
        """
        ...

    async def get_by_work_order(
        self, work_order_id: WorkOrderId, empresa_id: CompanyId
    ) -> list[TechnicalIntervention]:
        """Obtiene todas las intervenciones de una orden de trabajo.

        Args:
            work_order_id: Identificador de la orden de trabajo.
            empresa_id: Identificador de la empresa (tenant).

        Returns:
            Lista de intervenciones asociadas a la orden de trabajo.
        """
        ...

    async def get_by_technician(
        self, technician_id: UserId, empresa_id: CompanyId
    ) -> list[TechnicalIntervention]:
        """Obtiene todas las intervenciones realizadas por un técnico.

        Args:
            technician_id: Identificador del técnico.
            empresa_id: Identificador de la empresa (tenant).

        Returns:
            Lista de intervenciones realizadas por el técnico.
        """
        ...

    async def delete(self, id: InterventionId, empresa_id: CompanyId) -> None:
        """Elimina una intervención técnica por su ID y empresa.

        Args:
            id: Identificador único de la intervención.
            empresa_id: Identificador de la empresa (tenant).
        """
        ...

    async def list(
        self, empresa_id: CompanyId, offset: int = 0, limit: int = 100
    ) -> tuple[list[TechnicalIntervention], int]:
        """Lista todas las intervenciones de una empresa con paginación.

        Args:
            empresa_id: Identificador de la empresa (tenant).
            offset: Número de registros a omitir (por defecto 0).
            limit: Cantidad máxima de registros a retornar (por defecto 100).

        Returns:
            Una tupla con la lista de intervenciones y el total de registros.
        """
        ...
