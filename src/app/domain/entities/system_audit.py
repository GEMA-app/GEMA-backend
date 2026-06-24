from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional
from app.domain.exceptions.system_audit import SystemAuditException
from app.domain.value_objects import CompanyId, UserId  # VOs compartidos del proyecto


@dataclass
class SystemAudit:
    """
    Entidad rica de Dominio que representa un registro de auditoría del sistema.
    Completamente aislada de frameworks, Pydantic o SQLAlchemy.
    """
    id: Optional[int]
    empresa_id: CompanyId
    usuario_id: Optional[UserId]
    accion: str
    detalles: Dict[str, Any]
    ip_address: Optional[str]
    ocurrido_en: datetime

    @classmethod
    def create(
        cls,
        empresa_id: CompanyId,
        usuario_id: Optional[UserId],
        accion: str,
        detalles: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
    ) -> "SystemAudit":
        """
        Método fábrica para generar un nuevo registro de auditoría con sus invariantes.
        """
        return cls(
            id=None,  # Autogenerado por la infraestructura/BD más adelante
            empresa_id=empresa_id,
            usuario_id=usuario_id,
            accion=accion,
            detalles=detalles if detalles is not None else {},
            ip_address=ip_address,
            ocurrido_en=datetime.now(),
        )

    def __post_init__(self) -> None:
        """
        Protección de Invariantes: Reglas de negocio que jamás deben violarse.
        """
        if not self.accion or self.accion.strip() == "":
            raise SystemAuditException("La acción de la auditoría no puede estar vacía.")
        
        if self.empresa_id is None:
            raise SystemAuditException("La auditoría debe estar vinculada a una empresa válida.")