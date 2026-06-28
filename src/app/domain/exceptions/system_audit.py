import uuid

from app.domain.exceptions.base import DomainException


class SystemAuditException(DomainException):
    """Clase base para excepciones del módulo de auditoría de sistema."""
    pass


class SystemAuditNotFoundError(SystemAuditException):
    """Lanzada cuando un registro de auditoría específico no existe en la empresa."""

    def __init__(self, audit_id: uuid.UUID | int, empresa_id: str) -> None:
        self.audit_id = audit_id
        self.empresa_id = empresa_id
        self.message = f"No se encontró la auditoría con ID {audit_id} para la empresa {empresa_id}"
        super().__init__(self.message)

