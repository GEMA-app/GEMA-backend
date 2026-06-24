class SystemAuditException(Exception):
    """Excepción base para todos los errores del módulo de auditoría de sistema."""
    pass


class SystemAuditNotFoundError(SystemAuditException):
    """Se lanza cuando un registro de auditoría específico no existe en la empresa."""
    def __init__(self, auditoria_id: int, empresa_id: str):
        self.auditoria_id = auditoria_id
        self.empresa_id = empresa_id
        self.message = f"No se encontró la auditoría con ID {auditoria_id} para la empresa {empresa_id}"
        super().__init__(self.message)