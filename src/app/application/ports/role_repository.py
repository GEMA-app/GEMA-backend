from typing import Protocol

from app.domain.entities import Role
from app.domain.value_objects import CompanyId, RoleId, UserId


class RoleRepositoryPort(Protocol):
    """Puerto de repositorio para la persistencia, consulta y asignación de Roles."""

    async def save(self, role: Role) -> None:
        """Guarda o actualiza un rol en el repositorio."""
        ...

    async def get_by_id(self, id: RoleId, empresa_id: CompanyId) -> Role | None:
        """Busca un rol por su identificador único dentro de una empresa."""
        ...

    async def list_by_company(self, empresa_id: CompanyId) -> list[Role]:
        """Devuelve todos los roles asociados a una empresa."""
        ...

    async def delete(self, id: RoleId, empresa_id: CompanyId) -> None:
        """Elimina un rol por su identificador único dentro de una empresa."""
        ...

    async def assign_to_user(self, role_id: RoleId, user_id: UserId) -> None:
        """Asigna un rol a un usuario (tabla asociativa)."""
        ...

    async def revoke_from_user(self, role_id: RoleId, user_id: UserId) -> None:
        """Revoca un rol a un usuario."""
        ...

    async def get_user_roles(self, user_id: UserId, empresa_id: CompanyId) -> list[Role]:
        """Obtiene todos los roles asignados a un usuario dentro de una empresa."""
        ...
