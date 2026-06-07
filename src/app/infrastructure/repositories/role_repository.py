import uuid

from sqlalchemy import delete as sql_delete
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.role_repository import RoleRepositoryPort
from app.domain.entities import Permission, Role
from app.domain.events import DomainEvent
from app.domain.value_objects import CompanyId, RoleId, UserId
from app.infrastructure.db.models.role import PermissionModel, RoleModel, RoleUserModel
from app.infrastructure.repositories.base import SqlAlchemyRepository


class SqlAlchemyRoleRepository(SqlAlchemyRepository[RoleModel, Role, RoleId], RoleRepositoryPort):
    """Implementación en SQLAlchemy para el puerto de repositorio de Roles."""

    def __init__(
        self, session: AsyncSession, pending_events: list[DomainEvent] | None = None
    ) -> None:
        super().__init__(session, RoleModel, pending_events)


    async def save(self, entity: Role) -> None:
        """Persiste un rol preservando los UUIDs de permisos existentes."""
        existing_model = await self.session.get(RoleModel, entity.id.value)

        if existing_model is None:
            # Nuevo rol: generar UUIDs para permisos nuevos
            model = self._to_model(entity)
            await self.session.merge(model)
        else:
            # Actualización: mutar in-place
            existing_model.nombre = entity.nombre
            existing_model.descripcion = entity.descripcion

            # Sincronizar permisos por módulo
            existing_by_module = {p.modulo: p for p in existing_model.permisos}
            new_permisos = []

            for p in entity.permisos:
                existing_perm = existing_by_module.get(p.module)
                if existing_perm:
                    # Preservar UUID existente, actualizar valores
                    existing_perm.puede_ver = p.can_view
                    existing_perm.puede_crear = p.can_create
                    existing_perm.puede_editar = p.can_edit
                    existing_perm.puede_eliminar = p.can_delete
                    new_permisos.append(existing_perm)
                else:
                    # Permiso nuevo: generar UUID
                    new_permisos.append(
                        PermissionModel(
                            id=uuid.uuid4(),
                            empresa_id=entity.empresa_id.value,
                            rol_id=entity.id.value,
                            modulo=p.module,
                            puede_ver=p.can_view,
                            puede_crear=p.can_create,
                            puede_editar=p.can_edit,
                            puede_eliminar=p.can_delete,
                        )
                    )

            existing_model.permisos = new_permisos

        # Recolectar eventos (no se invoca super().save() para preservar UUIDs de permisos)
        self._collect_events(entity)


    def _to_model(self, entity: Role) -> RoleModel:
        # Se genera un UUID para permisos nuevos si no lo tuvieran,
        # pero como Permission es un Value Object de dominio, mapeamos a modelos ORM.
        permisos_models = [
            PermissionModel(
                id=uuid.uuid4(),
                empresa_id=entity.empresa_id.value,
                rol_id=entity.id.value,
                modulo=p.module,
                puede_ver=p.can_view,
                puede_crear=p.can_create,
                puede_editar=p.can_edit,
                puede_eliminar=p.can_delete,
            )
            for p in entity.permisos
        ]
        return RoleModel(
            id=entity.id.value,
            empresa_id=entity.empresa_id.value,
            nombre=entity.nombre,
            descripcion=entity.descripcion,
            permisos=permisos_models,
        )

    def _to_entity(self, model: RoleModel) -> Role:
        permisos = [
            Permission(
                module=p.modulo,
                can_view=p.puede_ver,
                can_create=p.puede_crear,
                can_edit=p.puede_editar,
                can_delete=p.puede_eliminar,
            )
            for p in model.permisos
        ]
        return Role(
            id=RoleId(model.id),
            empresa_id=CompanyId(model.empresa_id),
            nombre=model.nombre,
            descripcion=model.descripcion or "",
            permisos=permisos,
        )

    async def get_by_id(self, id: RoleId, empresa_id: CompanyId) -> Role | None:  # type: ignore[override]
        stmt = select(RoleModel).where(
            RoleModel.id == id.value, RoleModel.empresa_id == empresa_id.value
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_entity(model)

    async def list_by_company(self, empresa_id: CompanyId) -> list[Role]:
        stmt = select(RoleModel).where(RoleModel.empresa_id == empresa_id.value)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def delete(self, id: RoleId, empresa_id: CompanyId) -> None:  # type: ignore[override]
        stmt = sql_delete(RoleModel).where(
            RoleModel.id == id.value, RoleModel.empresa_id == empresa_id.value
        )
        await self.session.execute(stmt)

    async def assign_to_user(self, role_id: RoleId, user_id: UserId) -> None:
        from app.infrastructure.db.models.user import UserModel

        await self.session.flush()
        user_model = await self.session.get(UserModel, user_id.value)
        role_model = await self.session.get(RoleModel, role_id.value)

        if user_model and role_model:
            if role_model not in user_model.roles:
                user_model.roles.append(role_model)

    async def revoke_from_user(self, role_id: RoleId, user_id: UserId) -> None:
        from app.infrastructure.db.models.user import UserModel

        await self.session.flush()
        user_model = await self.session.get(UserModel, user_id.value)
        role_model = await self.session.get(RoleModel, role_id.value)

        if user_model and role_model:
            if role_model in user_model.roles:
                user_model.roles.remove(role_model)

    async def get_user_roles(self, user_id: UserId, empresa_id: CompanyId) -> list[Role]:
        stmt = (
            select(RoleModel)
            .join(RoleUserModel)
            .where(
                RoleUserModel.usuario_id == user_id.value, RoleModel.empresa_id == empresa_id.value
            )
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]
