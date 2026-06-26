"""Excepciones de dominio del módulo UsedPart (repuestos utilizados)."""

from decimal import Decimal

from app.domain.exceptions.base import DomainException


class UsedPartException(DomainException):
    """Excepción base para el módulo de repuestos utilizados."""
    pass


class UsedPartNotFoundError(UsedPartException):
    """Se lanza cuando un repuesto utilizado no existe."""
    def __init__(self, used_part_id: str) -> None:
        self.used_part_id = used_part_id
        super().__init__(f"Repuesto utilizado con ID '{used_part_id}' no encontrado.")


class UsedPartInvalidQuantityError(UsedPartException):
    """Se lanza cuando la cantidad usada es inválida (<= 0)."""
    def __init__(self, quantity: int) -> None:
        self.quantity = quantity
        super().__init__(f"La cantidad usada '{quantity}' debe ser mayor a 0.")


class UsedPartInvalidPriceError(UsedPartException):
    """Se lanza cuando el precio unitario es inválido (<= 0)."""
    def __init__(self, price: Decimal) -> None:
        self.price = price
        super().__init__(f"El precio unitario '{price}' debe ser mayor a 0.")
