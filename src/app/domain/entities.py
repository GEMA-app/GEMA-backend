from datetime import datetime, timezone
from typing import Optional
import uuid
from app.domain.exceptions import UserInactiveError
from app.domain.value_objects import Email, HashedPassword, UserId
from app.domain.events import DomainEvent, UserLoggedIn, UserRegistered


class User:
    """Entidad de dominio rica que representa a un usuario en el sistema."""

    def __init__(
        self,
        id: UserId,
        email: Email,
        hashed_password: HashedPassword,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ) -> None:
        self.id = id
        self.email = email
        self.hashed_password = hashed_password
        self.is_active = is_active
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at or datetime.now(timezone.utc)
        self._events: list[DomainEvent] = []

    @classmethod
    def register(cls, email: Email, hashed_password: HashedPassword) -> "User":
        """Fábrica de dominio para registrar un nuevo usuario y emitir el evento correspondiente."""
        user_id = UserId(value=uuid.uuid4())
        user = cls(id=user_id, email=email, hashed_password=hashed_password, is_active=True)
        user._events.append(UserRegistered(user_id=str(user.id), email=user.email.value))
        return user

    def login(self) -> None:
        """Registra el inicio de sesión del usuario, validando sus invariantes de estado."""
        if not self.is_active:
            raise UserInactiveError(f"El usuario {self.email.value} está inactivo.")
        self._events.append(UserLoggedIn(user_id=str(self.id), email=self.email.value))

    def pull_events(self) -> list[DomainEvent]:
        """Devuelve los eventos de dominio acumulados y limpia la lista interna."""
        events = self._events.copy()
        self._events.clear()
        return events
