"""Entidad Role — rol RBAC con permisos granularizados por módulo."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime

from app.domain.entities.permission import Permission
from app.domain.enums import PermissionModule
from app.domain.events import DomainEvent, EventProducer, RoleAssigned, RoleRevoked
from app.domain.exceptions import EmptyRoleNameError
from app.domain.value_objects import CompanyId, RoleId, UserId


@dataclass
class Role(EventProducer):
    """Entidad con comportamiento (Rich Entity) que representa un Rol
    con permisos asignados para cada módulo.
    """

    id: RoleId
    empresa_id: CompanyId
    nombre: str
    descripcion: str
    permisos: list[Permission] = field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None
    _events: list[DomainEvent] = field(default_factory=list, init=False, repr=False)

    @classmethod
    def create(
        cls,
        empresa_id: CompanyId,
        nombre: str,
        descripcion: str,
        permisos: list[Permission] | None = None,
    ) -> "Role":
        """Crea un nuevo rol de dominio.

        Args:
            empresa_id: Identificador de la empresa a la que pertenece el rol.
            nombre: Nombre del rol (no puede estar vacío).
            descripcion: Descripción del rol.
            permisos: Lista de permisos a asignar al rol (opcional).

        Returns:
            La nueva entidad Role creada.

        Raises:
            EmptyRoleNameError: Si el nombre del rol está vacío o solo contiene espacios.
        """
        if not nombre or not nombre.strip():
            raise EmptyRoleNameError("El nombre del rol no puede estar vacío.")
        return cls(
            id=RoleId(uuid.uuid4()),
            empresa_id=empresa_id,
            nombre=nombre.strip(),
            descripcion=descripcion,
            permisos=permisos or [],
        )

    @classmethod
    def create_admin(cls, empresa_id: CompanyId) -> "Role":
        """Crea un rol de Administrador con todos los permisos.

        Args:
            empresa_id: Identificador de la empresa para la cual crear el rol.

        Returns:
            El nuevo rol de Administrador con todos los permisos habilitados.
        """
        permisos = [
            Permission(
                module=module, can_view=True, can_create=True, can_edit=True, can_delete=True
            )
            for module in PermissionModule
        ]
        return cls(
            id=RoleId(uuid.uuid4()),
            empresa_id=empresa_id,
            nombre="Administrador",
            descripcion="Administrador del sistema con acceso completo a todos los módulos.",
            permisos=permisos,
        )

    def has_permission(self, module: PermissionModule, action: str) -> bool:
        """Verifica si el rol tiene el permiso solicitado para un módulo.

        Args:
            module: El módulo de permiso a consultar.
            action: La acción a verificar. Puede ser 'view', 'create', 'edit', 'delete'.

        Returns:
            True si el rol tiene el permiso solicitado, False en caso contrario.
        """
        for p in self.permisos:
            if p.module == module:
                if action == "view":
                    return p.can_view
                elif action == "create":
                    return p.can_create
                elif action == "edit":
                    return p.can_edit
                elif action == "delete":
                    return p.can_delete
        return False

    def grant(
        self,
        module: PermissionModule,
        can_view: bool = False,
        can_create: bool = False,
        can_edit: bool = False,
        can_delete: bool = False,
    ) -> None:
        """Otorga o actualiza permisos para un módulo específico.

        Args:
            module: El módulo sobre el cual otorgar permisos.
            can_view: Permiso de visualización.
            can_create: Permiso de creación.
            can_edit: Permiso de edición.
            can_delete: Permiso de eliminación.
        """
        new_perm = Permission(
            module=module,
            can_view=can_view,
            can_create=can_create,
            can_edit=can_edit,
            can_delete=can_delete,
        )
        for i, p in enumerate(self.permisos):
            if p.module == module:
                self.permisos[i] = new_perm
                return
        self.permisos.append(new_perm)

    def record_assignment(self, user_id: UserId) -> None:
        """Registra la asignación de este rol a un usuario.

        Args:
            user_id: Identificador del usuario al que se asigna el rol.
        """
        self._events.append(
            RoleAssigned(
                user_id=str(user_id.value),
                role_id=str(self.id.value),
                empresa_id=str(self.empresa_id.value),
            )
        )

    def record_revocation(self, user_id: UserId) -> None:
        """Registra la revocación de este rol de un usuario.

        Args:
            user_id: Identificador del usuario al que se revoca el rol.
        """
        self._events.append(
            RoleRevoked(
                user_id=str(user_id.value),
                role_id=str(self.id.value),
                empresa_id=str(self.empresa_id.value),
            )
        )

    def pull_events(self) -> list[DomainEvent]:
        """Devuelve los eventos de dominio acumulados y limpia la lista interna."""
        events = self._events.copy()
        self._events.clear()
        return events
