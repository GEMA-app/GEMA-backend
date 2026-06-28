import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from app.domain.exceptions.system_audit import SystemAuditException
from app.domain.value_objects import CompanyId, UserId


@dataclass
class SystemAudit:
    """Entidad rica de Dominio que representa un registro de auditoría del sistema.

    Completamente aislada de frameworks, Pydantic o SQLAlchemy.
    """

    id: uuid.UUID | None
    empresa_id: CompanyId
    usuario_id: UserId | None
    accion: str
    detalles: dict[str, Any]
    ip_address: str | None
    ocurrido_en: datetime


    @classmethod
    def create(
        cls,
        empresa_id: CompanyId,
        usuario_id: UserId | None,
        accion: str,
        detalles: dict[str, Any] | None = None,
        ip_address: str | None = None,
    ) -> "SystemAudit":
        """Crea un nuevo registro de auditoría validando invariantes de dominio.

        Args:
            empresa_id: Identificador de la empresa propietaria.
            usuario_id: Identificador opcional del usuario que ejecutó la acción.
            accion: Nombre de la acción registrada.
            detalles: Metadatos adicionales de la auditoría.
            ip_address: Dirección IP desde donde se ejecutó la acción.

        Returns:
            Nueva instancia de SystemAudit con los valores provistos.
        """
        return cls(
            id=None,  # Autogenerado por la infraestructura/BD
            empresa_id=empresa_id,
            usuario_id=usuario_id,
            accion=accion,
            detalles=detalles if detalles is not None else {},
            ip_address=ip_address,
            ocurrido_en=datetime.now(),
        )

    def __post_init__(self) -> None:
        """Valida invariantes de negocio tras la inicialización.

        Raises:
            SystemAuditException: Si la acción está vacía o el empresa_id es nulo.
        """
        if not self.accion or self.accion.strip() == "":
            raise SystemAuditException("La acción de la auditoría no puede estar vacía.")

        if self.empresa_id is None:
            raise SystemAuditException("La auditoría debe estar vinculada a una empresa válida.")
