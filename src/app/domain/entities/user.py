"""Entidad User del sistema."""

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime

from app.domain.entities.role import Role
from app.domain.events import (
    DomainEvent,
    EventProducer,
    PasswordChanged,
    PasswordResetCompleted,
    PasswordResetInitiated,
    UserActivated,
    UserDeactivated,
    UserLoggedIn,
    UserRegistered,
)
from app.domain.exceptions import UserInactiveError
from app.domain.value_objects import CompanyId, Email, HashedPassword, UserId


@dataclass
class User(EventProducer):
    """Entidad con comportamiento (Rich Entity) que representa a un usuario en el sistema."""

    id: UserId
    email: Email
    password_hash: HashedPassword
    empresa_id: CompanyId
    nombre: str
    telefono: str | None = None
    activo: bool = True
    roles: list[Role] = field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None
    _events: list[DomainEvent] = field(default_factory=list, init=False, repr=False)

    def __post_init__(self) -> None:
        """Inicializa los campos de fecha por defecto si no están definidos."""
        if self.created_at is None:
            self.created_at = datetime.now(UTC)
        if self.updated_at is None:
            self.updated_at = datetime.now(UTC)

    @classmethod
    def register(
        cls,
        email: Email,
        password_hash: HashedPassword,
        empresa_id: CompanyId,
        nombre: str,
        telefono: str | None = None,
        company_name: str = "",
    ) -> "User":
        """Fábrica de dominio para registrar un nuevo usuario y emitir el evento correspondiente.

        Args:
            email: Dirección de correo electrónico del usuario.
            password_hash: Hash de la contraseña del usuario.
            empresa_id: Identificador de la empresa (tenant) a la que pertenece.
            nombre: Nombre completo del usuario.
            telefono: Número de teléfono del usuario (opcional).
            company_name: Nombre de la empresa para el evento de registro (opcional).

        Returns:
            La nueva entidad User creada con el evento UserRegistered emitido.
        """
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
        user._events.append(
            UserRegistered(
                user_id=str(user.id),
                email=user.email.value,
                nombre=nombre,
                empresa_id=str(empresa_id),
                company_name=company_name,
            )
        )
        return user

    def login(self) -> None:
        """Inicia sesión validando que el usuario esté activo.

        Raises:
            UserInactiveError: Si el usuario está marcado como inactivo.
        """
        if not self.activo:
            raise UserInactiveError(f"El usuario {self.email.value} está inactivo.")
        self._events.append(UserLoggedIn(user_id=str(self.id), email=self.email.value))

    def change_password(self, new_hashed: str) -> None:
        """Cambia la contraseña del usuario y emite PasswordChanged.

        Args:
            new_hashed: El nuevo hash de contraseña a asignar.
        """
        self.password_hash = HashedPassword(value=new_hashed)
        self.updated_at = datetime.now(UTC)
        self._events.append(PasswordChanged(user_id=str(self.id), email=self.email.value))

    def deactivate(self) -> None:
        """Desactiva el usuario. No puede iniciar sesión si está inactivo."""
        self.activo = False
        self.updated_at = datetime.now(UTC)
        self._events.append(UserDeactivated(user_id=str(self.id), email=self.email.value))

    def activate(self) -> None:
        """Activa el usuario. Puede iniciar sesión."""
        self.activo = True
        self.updated_at = datetime.now(UTC)
        self._events.append(UserActivated(user_id=str(self.id), email=self.email.value))

    def request_password_reset(self) -> None:
        """Emite PasswordResetInitiated como evento de auditoría.

        El email con el raw_token se envía directamente desde el use case
        para evitar que el token se serialice en una tabla outbox.
        """
        self._events.append(PasswordResetInitiated(user_id=str(self.id), email=self.email.value))

    def complete_password_reset(self, new_hashed: str) -> None:
        """Completa el restablecimiento de clave y emite PasswordResetCompleted.

        Args:
            new_hashed: El nuevo hash de contraseña a asignar.
        """
        self.password_hash = HashedPassword(value=new_hashed)
        self.updated_at = datetime.now(UTC)
        self._events.append(PasswordResetCompleted(user_id=str(self.id), email=self.email.value))

    def pull_events(self) -> list[DomainEvent]:
        """Devuelve los eventos de dominio acumulados y limpia la lista interna.

        Returns:
            La lista de eventos de dominio acumulados, vaciando la lista interna.
        """
        events = self._events.copy()
        self._events.clear()
        return events
