"""Excepciones de dominio del módulo PlanExecution (Ejecución de Plan)."""

from app.domain.exceptions.base import DomainException


class PlanExecutionException(DomainException):
    """Error base del módulo de ejecuciones de plan."""


class PlanExecutionNotFoundError(PlanExecutionException):
    """La ejecución de plan solicitada no existe en la empresa."""

    def __init__(self, execution_id: str, empresa_id: str) -> None:
        self.execution_id = execution_id
        self.empresa_id = empresa_id
        self.message = (
            f"Ejecución de plan '{execution_id}' no encontrada en la empresa '{empresa_id}'."
        )
        super().__init__(self.message)


class PlanExecutionObservationsEmptyError(PlanExecutionException):
    """Las observaciones no pueden ser solo espacios en blanco."""

    def __init__(self) -> None:
        self.message = "Las observaciones no pueden estar vacías o ser solo espacios."
        super().__init__(self.message)
