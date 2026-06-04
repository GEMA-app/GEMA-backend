import uuid
from dataclasses import dataclass, field

from app.domain.entities.permission import Permission
from app.domain.enums import PermissionModule
from app.domain.value_objects import CompanyId, RoleId


@dataclass
class Role:
    """Entidad que representa un Rol con permisos asignados para cada módulo."""
    id: RoleId
    empresa_id: CompanyId
    nombre: str
    descripcion: str
    permisos: list[Permission] = field(default_factory=list)

    @classmethod
    def create(
        cls,
        empresa_id: CompanyId,
        nombre: str,
        descripcion: str,
        permisos: list[Permission] | None = None
    ) -> "Role":
        """Crea un nuevo rol de dominio."""
        if not nombre or not nombre.strip():
            raise ValueError("El nombre del rol no puede estar vacío.")
        return cls(
            id=RoleId(uuid.uuid4()),
            empresa_id=empresa_id,
            nombre=nombre.strip(),
            descripcion=descripcion,
            permisos=permisos or []
        )

    @classmethod
    def create_admin(cls, empresa_id: CompanyId) -> "Role":
        """Crea un rol de Administrador con todos los permisos."""
        permisos = [
            Permission(
                module=module,
                can_view=True,
                can_create=True,
                can_edit=True,
                can_delete=True
            )
            for module in PermissionModule
        ]
        return cls(
            id=RoleId(uuid.uuid4()),
            empresa_id=empresa_id,
            nombre="Administrador",
            descripcion="Administrador del sistema con acceso completo a todos los módulos.",
            permisos=permisos
        )

    def has_permission(self, module: PermissionModule, action: str) -> bool:
        """Verifica si el rol tiene el permiso solicitado para un módulo.

        action puede ser: 'view', 'create', 'edit', 'delete'
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
        can_delete: bool = False
    ) -> None:
        """Otorga o actualiza permisos para un módulo específico."""
        new_perm = Permission(
            module=module,
            can_view=can_view,
            can_create=can_create,
            can_edit=can_edit,
            can_delete=can_delete
        )
        # Reemplazar si ya existe
        for i, p in enumerate(self.permisos):
            if p.module == module:
                self.permisos[i] = new_perm
                return
        self.permisos.append(new_perm)
