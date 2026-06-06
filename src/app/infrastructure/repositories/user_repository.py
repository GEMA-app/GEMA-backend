from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.repository import UserRepositoryPort
from app.domain.entities import User
from app.domain.value_objects import CompanyId, Email, HashedPassword, UserId
from app.infrastructure.db.models import UserModel
from app.infrastructure.repositories.base import SqlAlchemyRepository


class SqlAlchemyUserRepository(
    SqlAlchemyRepository[UserModel, User, UserId], UserRepositoryPort
):
    """Implementación de UserRepositoryPort utilizando la clase base SqlAlchemyRepository."""

    def __init__(self, session: AsyncSession) -> None:
        """Inicializa el repositorio de usuarios con la sesión de base de datos."""
        super().__init__(session, UserModel)

    async def get_by_email(self, email: Email) -> User | None:
        """Busca un usuario por email globalmente en la base de datos."""
        stmt = select(UserModel).where(UserModel.email == email.value)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_entity(model)

    async def get_by_email_and_company(self, email: Email, empresa_id: CompanyId) -> User | None:
        """Busca un usuario por email dentro de una empresa específica."""
        stmt = select(UserModel).where(
            UserModel.email == email.value, UserModel.empresa_id == empresa_id.value
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_entity(model)

    def _to_model(self, entity: User) -> UserModel:
        return UserModel(
            id=entity.id.value,
            email=entity.email.value,
            password_hash=entity.password_hash.value,
            empresa_id=entity.empresa_id.value,
            nombre=entity.nombre,
            telefono=entity.telefono,
            activo=entity.activo,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    def _to_entity(self, model: UserModel) -> User:
        from app.domain.entities import Permission, Role
        from app.domain.value_objects import RoleId

        roles = [
            Role(
                id=RoleId(rm.id),
                empresa_id=CompanyId(rm.empresa_id),
                nombre=rm.nombre,
                descripcion=rm.descripcion or "",
                permisos=[
                    Permission(
                        module=p.modulo,
                        can_view=p.puede_ver,
                        can_create=p.puede_crear,
                        can_edit=p.puede_editar,
                        can_delete=p.puede_eliminar,
                    )
                    for p in rm.permisos
                ],
            )
            for rm in model.roles
        ]
        return User(
            id=UserId(value=model.id),
            email=Email(value=model.email),
            password_hash=HashedPassword(value=model.password_hash),
            empresa_id=CompanyId(model.empresa_id),
            nombre=model.nombre,
            telefono=model.telefono,
            activo=model.activo,
            roles=roles,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
