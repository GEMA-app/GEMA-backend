from typing import Any, Self
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.infrastructure.db.session import async_session_factory
from app.infrastructure.repositories.user_repository import SqlAlchemyUserRepository


class SqlAlchemyUnitOfWork(UnitOfWorkPort):
    """Implementación de UnitOfWorkPort utilizando SQLAlchemy 2.0 y AsyncSession."""

    def __init__(
        self, session_factory: async_sessionmaker[AsyncSession] = async_session_factory
    ) -> None:
        self.session_factory = session_factory

    async def __aenter__(self) -> Self:
        """Inicia la sesión asíncrona y construye los repositorios asociados a ella."""
        self.session = self.session_factory()
        self.users = SqlAlchemyUserRepository(self.session)
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, tb: Any) -> None:
        """Cierra la sesión de base de datos, ejecutando rollback si ocurrió una excepción."""
        try:
            if exc_type is not None:
                await self.rollback()
        finally:
            await self.session.close()

    async def commit(self) -> None:
        """Confirma la transacción actual en la base de datos."""
        await self.session.commit()

    async def rollback(self) -> None:
        """Deshace los cambios pendientes en la transacción actual."""
        await self.session.rollback()
