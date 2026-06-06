import uuid
from datetime import UTC, datetime

from app.domain.entities.role import Role
from app.domain.events import DomainEvent, UserLoggedIn, UserRegistered
from app.domain.exceptions import UserInactiveError
from app.domain.value_objects import CompanyId, Email, HashedPassword, UserId


class User:
    """Entidad con comportamiento (Rich Entity) que representa a un usuario en el sistema."""

    def __init__(
        self,
        id: UserId,
        email: Email,
        password_hash: HashedPassword,
        empresa_id: CompanyId,
        nombre: str,
        telefono: str | None = None,
        activo: bool = True,
        roles: list[Role] | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        self.id = id
        self.email = email
        self.password_hash = password_hash
        self.empresa_id = empresa_id
        self.nombre = nombre
        self.telefono = telefono
        self.activo = activo
        self.roles = roles or []
        self.created_at = created_at or datetime.now(UTC)
        self.updated_at = updated_at or datetime.now(UTC)
        self._events: list[DomainEvent] = []

    @classmethod
    def register(
        cls,
        email: Email,
        password_hash: HashedPassword,
        empresa_id: CompanyId,
        nombre: str,
        telefono: str | None = None,
    ) -> "User":
        """Fábrica de dominio para registrar un nuevo usuario y emitir el evento correspondiente."""
        user_id = UserId(value=uuid.uuid4())
        user = cls(
            id=user_id,
            email=email,
            password_hash=password_hash,
            empresa_id=empresa_id,
            nombre=nombre,
            telefono=telefono,
            activo=True,
            roles=[],
        )
        user._events.append(UserRegistered(user_id=str(user.id), email=user.email.value))
        return user

    def login(self) -> None:
        """Registra el inicio de sesión del usuario, validando sus invariantes de estado."""
        if not self.activo:
            raise UserInactiveError(f"El usuario {self.email.value} está inactivo.")
        self._events.append(UserLoggedIn(user_id=str(self.id), email=self.email.value))

    def pull_events(self) -> list[DomainEvent]:
        """Devuelve los eventos de dominio acumulados y limpia la lista interna."""
        events = self._events.copy()
        self._events.clear()
        return events
