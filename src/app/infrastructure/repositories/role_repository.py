import uuid

from sqlalchemy import delete as sql_delete
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.role_repository import RoleRepositoryPort
from app.domain.entities import Permission, Role
from app.domain.value_objects import CompanyId, RoleId, UserId
from app.infrastructure.db.models.role import PermissionModel, RoleModel, RoleUserModel
from app.infrastructure.repositories.base import SqlAlchemyRepository


class SqlAlchemyRoleRepository(SqlAlchemyRepository[RoleModel, Role, RoleId], RoleRepositoryPort):
    """Implementación en SQLAlchemy para el puerto de repositorio de Roles."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, RoleModel)

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
                puede_eliminar=p.can_delete
            )
            for p in entity.permisos
        ]
        return RoleModel(
            id=entity.id.value,
            empresa_id=entity.empresa_id.value,
            nombre=entity.nombre,
            descripcion=entity.descripcion,
            permisos=permisos_models
        )

    def _to_entity(self, model: RoleModel) -> Role:
        permisos = [
            Permission(
                module=p.modulo,
                can_view=p.puede_ver,
                can_create=p.puede_crear,
                can_edit=p.puede_editar,
                can_delete=p.puede_eliminar
            )
            for p in model.permisos
        ]
        return Role(
            id=RoleId(model.id),
            empresa_id=CompanyId(model.empresa_id),
            nombre=model.nombre,
            descripcion=model.descripcion or "",
            permisos=permisos
        )

    async def get_by_id(self, id: RoleId, empresa_id: CompanyId) -> Role | None:  # type: ignore[override]
        stmt = select(RoleModel).where(
            RoleModel.id == id.value,
            RoleModel.empresa_id == empresa_id.value
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
            RoleModel.id == id.value,
            RoleModel.empresa_id == empresa_id.value
        )
        await self.session.execute(stmt)

    async def assign_to_user(self, role_id: RoleId, user_id: UserId) -> None:
        stmt = select(RoleUserModel).where(
            RoleUserModel.rol_id == role_id.value,
            RoleUserModel.usuario_id == user_id.value
        )
        res = await self.session.execute(stmt)
        exists = res.scalar_one_or_none()
        if not exists:
            association = RoleUserModel(
                usuario_id=user_id.value,
                rol_id=role_id.value
            )
            self.session.add(association)

    async def revoke_from_user(self, role_id: RoleId, user_id: UserId) -> None:
        stmt = sql_delete(RoleUserModel).where(
            RoleUserModel.rol_id == role_id.value,
            RoleUserModel.usuario_id == user_id.value
        )
        await self.session.execute(stmt)

    async def get_user_roles(self, user_id: UserId, empresa_id: CompanyId) -> list[Role]:
        stmt = select(RoleModel).join(RoleUserModel).where(
            RoleUserModel.usuario_id == user_id.value,
            RoleModel.empresa_id == empresa_id.value
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]
