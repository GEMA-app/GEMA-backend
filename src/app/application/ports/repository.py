from typing import Optional, Protocol
from app.domain.entities import User
from app.domain.value_objects import Email, UserId


class UserRepositoryPort(Protocol):
    """Puerto de repositorio para la persistencia y consulta de entidades User."""

    async def save(self, user: User) -> None:
        """Guarda o actualiza un usuario en el repositorio sin confirmar la transacción."""
        ...

    async def get_by_email(self, email: Email) -> Optional[User]:
        """Busca un usuario por su dirección de correo electrónico."""
        ...

    async def get_by_id(self, id: UserId) -> Optional[User]:
        """Busca un usuario por su identificador único."""
        ...
