from typing import Any, Dict, List, Optional, Protocol, Tuple
from app.domain.entities.system_audit import SystemAudit
from app.domain.value_objects import CompanyId


class SystemAuditRepositoryPort(Protocol):
    """Contrato estructural (Puerto) para el repositorio de auditorías."""

    async def get_all_by_empresa(
        self, 
        empresa_id: CompanyId, 
        offset: int, 
        limit: int, 
        filters: Dict[str, Any]
    ) -> Tuple[List[SystemAudit], int]:
        """Obtiene la lista de entidades de dominio filtradas y el total."""
        ...

    async def get_by_id(
        self, empresa_id: CompanyId, auditoria_id: int
    ) -> Optional[SystemAudit]:
        """Obtiene una entidad de auditoría específica por ID."""
        ...