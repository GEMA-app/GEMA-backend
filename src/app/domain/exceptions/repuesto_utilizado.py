from app.domain.exceptions.base import DomainException

class RepuestoUtilizadoException(DomainException):
    """Excepción base para el módulo de repuestos utilizados."""
    pass

class RepuestoUtilizadoNotFoundError(RepuestoUtilizadoException):
    """Se lanza cuando un repuesto utilizado no existe."""
    def __init__(self, repuesto_utilizado_id: str):
        self.repuesto_utilizado_id = repuesto_utilizado_id
        super().__init__(f"Repuesto utilizado con ID '{repuesto_utilizado_id}' no encontrado.")

class RepuestoUtilizadoCantidadInvalidaError(RepuestoUtilizadoException):
    """Se lanza cuando la cantidad usada es inválida (<= 0)."""
    def __init__(self, cantidad: int):
        self.cantidad = cantidad
        super().__init__(f"La cantidad usada '{cantidad}' debe ser mayor a 0.")

class RepuestoUtilizadoPrecioInvalidoError(RepuestoUtilizadoException):
    """Se lanza cuando el precio unitario es inválido (<= 0)."""
    def __init__(self, precio: float):
        self.precio = precio
        super().__init__(f"El precio unitario '{precio}' debe ser mayor a 0.")
