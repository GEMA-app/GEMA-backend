from typing import Protocol

from app.domain.entities import User
from app.domain.value_objects import CompanyId, Email, UserId


class UserRepositoryPort(Protocol):
    """Puerto de repositorio para la persistencia y consulta de entidades User."""

    async def save(self, user: User) -> None:
        """Guarda o actualiza un usuario en el repositorio sin confirmar la transacción."""
        ...

    async def get_by_email(self, email: Email) -> User | None:
        """Busca un usuario por su dirección de correo electrónico globalmente."""
        ...

    async def get_by_email_and_company(self, email: Email, empresa_id: CompanyId) -> User | None:
        """Busca un usuario por email dentro de una empresa específica.

        NOTE: Reservado para flujo de invitación (Sprint futuro).
        """
        ...

    async def get_by_id(self, id: UserId) -> User | None:
        """Busca un usuario por su identificador único."""
        ...

    async def get_by_id_and_company(self, id: UserId, empresa_id: CompanyId) -> User | None:
        """Busca un usuario por su ID garantizando que pertenezca a la empresa indicada.

        Previene IDOR: un admin de empresa A no puede consultar usuarios de empresa B.
        """
        ...

    async def list_by_company(self, empresa_id: CompanyId) -> list[User]:
        """Retorna todos los usuarios pertenecientes a una empresa."""
        ...
