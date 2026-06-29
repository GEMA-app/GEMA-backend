"""Repositorio de usuarios con SQLAlchemy asíncrono."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.repository import UserRepositoryPort
from app.domain.entities import User
from app.domain.events import DomainEvent
from app.domain.value_objects import CompanyId, Email, HashedPassword, UserId
from app.infrastructure.db.models import UserModel
from app.infrastructure.repositories.base import SqlAlchemyRepository


class SqlAlchemyUserRepository(
    SqlAlchemyRepository[UserModel, User, UserId], UserRepositoryPort
):
    """Implementación de UserRepositoryPort utilizando la clase base SqlAlchemyRepository."""

    def __init__(
        self, session: AsyncSession, pending_events: list[DomainEvent] | None = None
    ) -> None:
        """Inicializa el repositorio de usuarios con la sesión de base de datos.

        Args:
            session: Sesión asíncrona de SQLAlchemy.
            pending_events: Lista para la acumulación de eventos de dominio.
        """
        super().__init__(session, UserModel, pending_events)


    async def get_by_email(self, email: Email) -> User | None:
        """Busca un usuario por email globalmente en la base de datos.

        Nota: En el modelo SaaS actual, el email es único por tenant (uq_usuarios_empresa_email).
        Esta búsqueda global es correcta para el flujo de login donde el tenant no se conoce
        a priori.

        Args:
            email: Objeto de valor que representa el correo del usuario.

        Returns:
            La entidad User si fue encontrada; de lo contrario, None.
        """
        stmt = select(UserModel).where(UserModel.email == email.value)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_entity(model)

    async def get_by_email_and_company(self, email: Email, empresa_id: CompanyId) -> User | None:
        """Busca un usuario por email dentro de una empresa específica.

        NOTA: Reservado para flujo de invitación (Sprint futuro).

        Args:
            email: Objeto de valor que representa el correo del usuario.
            empresa_id: Identificador de la empresa.

        Returns:
            La entidad User si fue encontrada; de lo contrario, None.
        """
        stmt = select(UserModel).where(
            UserModel.email == email.value, UserModel.empresa_id == empresa_id.value
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_entity(model)

    async def list_by_company(self, empresa_id: CompanyId) -> list[User]:
        """Retorna todos los usuarios pertenecientes a una empresa.

        Args:
            empresa_id: Identificador de la empresa (tenant).

        Returns:
            Lista de entidades User asociadas a la empresa.
        """
        stmt = select(UserModel).where(UserModel.empresa_id == empresa_id.value)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def get_by_id(self, id: UserId) -> User | None:
        """Busca un usuario por ID.

        Nota: El aislamiento de tenant (tenant isolation) para la búsqueda de usuario
        por ID se garantiza en la capa de presentación (dependencies.py y endpoints)
        mediante la validación de que el empresa_id del token JWT coincide con el de la petición,
        o porque el ID consultado proviene directamente del token JWT ('sub').

        Args:
            id: Identificador del usuario.

        Returns:
            La entidad User si fue encontrada; de lo contrario, None.
        """
        return await super().get_by_id(id)

    async def get_by_id_and_company(self, id: UserId, empresa_id: CompanyId) -> User | None:
        """Busca un usuario por ID garantizando que pertenezca a la empresa indicada.

        Previene IDOR: impide que un admin de empresa A acceda a usuarios de empresa B.

        Args:
            id: Identificador del usuario.
            empresa_id: Identificador de la empresa (tenant).

        Returns:
            La entidad User si fue encontrada dentro del tenant; de lo contrario, None.
        """
        stmt = select(UserModel).where(
            UserModel.id == id.value,
            UserModel.empresa_id == empresa_id.value,
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
