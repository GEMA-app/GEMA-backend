from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.application.ports.repository import UserRepositoryPort
from app.domain.entities import User
from app.domain.value_objects import Email, HashedPassword, UserId
from app.infrastructure.db.models import UserModel


class SqlAlchemyUserRepository(UserRepositoryPort):
    """Implementación de UserRepositoryPort utilizando SQLAlchemy 2.0 y AsyncSession."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self, user: User) -> None:
        """Persiste o actualiza el modelo ORM en la sesión actual sin confirmar la transacción."""
        model = self._to_model(user)
        await self.session.merge(model)

    async def get_by_email(self, email: Email) -> Optional[User]:
        """Busca un usuario por email en la base de datos y lo mapea a la entidad de dominio."""
        stmt = select(UserModel).where(UserModel.email == email.value)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_entity(model)

    async def get_by_id(self, id: UserId) -> Optional[User]:
        """Busca un usuario por ID en la base de datos y lo mapea a la entidad de dominio."""
        stmt = select(UserModel).where(UserModel.id == id.value)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_entity(model)

    def _to_model(self, user: User) -> UserModel:
        return UserModel(
            id=user.id.value,
            email=user.email.value,
            hashed_password=user.hashed_password.value,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    def _to_entity(self, model: UserModel) -> User:
        return User(
            id=UserId(value=model.id),
            email=Email(value=model.email),
            hashed_password=HashedPassword(value=model.hashed_password),
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
