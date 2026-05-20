from typing import Any, Protocol, Self
from app.application.ports.repository import UserRepositoryPort


class UnitOfWorkPort(Protocol):
    """Puerto para el patrón Unit of Work, gestionando transacciones y repositorios."""

    users: UserRepositoryPort

    async def __aenter__(self) -> Self:
        """Inicia el contexto transaccional asíncrono."""
        ...

    async def __aexit__(self, exc_type: Any, exc_val: Any, tb: Any) -> None:
        """Cierra el contexto, ejecutando un rollback automático en caso de excepción."""
        ...

    async def commit(self) -> None:
        """Confirma los cambios pendientes en la base de datos."""
        ...

    async def rollback(self) -> None:
        """Deshace los cambios no confirmados en la transacción actual."""
        ...
