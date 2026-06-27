"""Excepciones de dominio del módulo MaintenancePlan (Plan de Mantenimiento)."""

from app.domain.exceptions.base import DomainException


class MaintenancePlanException(DomainException):
    """Error base del módulo de planes de mantenimiento."""


class MaintenancePlanNotFoundError(MaintenancePlanException):
    """El plan de mantenimiento solicitado no existe en la empresa."""

    def __init__(self, plan_id: str, empresa_id: str) -> None:
        self.plan_id = plan_id
        self.empresa_id = empresa_id
        self.message = (
            f"Plan de mantenimiento '{plan_id}' no encontrado en la empresa '{empresa_id}'."
        )
        super().__init__(self.message)


class MaintenancePlanNameEmptyError(MaintenancePlanException):
    """El nombre del plan de mantenimiento no puede estar vacío."""

    def __init__(self) -> None:
        self.message = "El nombre del plan de mantenimiento no puede estar vacío."
        super().__init__(self.message)


class MaintenancePlanIntervalError(MaintenancePlanException):
    """El intervalo en días debe ser mayor a cero."""

    def __init__(self, intervalo: int) -> None:
        self.message = f"El intervalo en días debe ser mayor a cero, se recibió: {intervalo}."
        super().__init__(self.message)


class MaintenancePlanDueDateError(MaintenancePlanException):
    """La fecha de próxima ejecución es requerida."""

    def __init__(self) -> None:
        self.message = "La fecha de próxima ejecución es requerida."
        super().__init__(self.message)
