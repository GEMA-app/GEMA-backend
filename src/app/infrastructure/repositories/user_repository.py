
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.repository import UserRepositoryPort
from app.domain.entities import User
from app.domain.value_objects import CompanyId, Email, HashedPassword, UserId
from app.infrastructure.db.models import UserModel


class SqlAlchemyUserRepository(UserRepositoryPort):
    """Implementación de UserRepositoryPort utilizando SQLAlchemy 2.0 y AsyncSession."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self, user: User) -> None:
        """Persiste o actualiza el modelo ORM en la sesión actual sin confirmar la transacción."""
        model = self._to_model(user)
        await self.session.merge(model)

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
            UserModel.email == email.value,
            UserModel.empresa_id == empresa_id.value
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_entity(model)

    async def get_by_id(self, id: UserId) -> User | None:
        """Busca un usuario por ID en la base de datos."""
        stmt = select(UserModel).where(UserModel.id == id.value)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_entity(model)

    def _to_model(self, user: User) -> UserModel:
        from app.infrastructure.db.models.role import RoleModel
        roles_models = [
            RoleModel(
                id=r.id.value,
                empresa_id=r.empresa_id.value,
                nombre=r.nombre,
                descripcion=r.descripcion
            )
            for r in user.roles
        ]
        return UserModel(
            id=user.id.value,
            email=user.email.value,
            hashed_password=user.hashed_password.value,
            empresa_id=user.empresa_id.value,
            nombre=user.nombre,
            telefono=user.telefono,
            activo=user.is_active,
            roles=roles_models,
            created_at=user.created_at,
            updated_at=user.updated_at,
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
                        can_delete=p.puede_eliminar
                    )
                    for p in rm.permisos
                ]
            )
            for rm in model.roles
        ]
        return User(
            id=UserId(value=model.id),
            email=Email(value=model.email),
            hashed_password=HashedPassword(value=model.hashed_password),
            empresa_id=CompanyId(model.empresa_id),
            nombre=model.nombre,
            telefono=model.telefono,
            is_active=model.activo,
            roles=roles,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
