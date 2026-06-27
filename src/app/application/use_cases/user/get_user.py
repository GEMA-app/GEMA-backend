"""Caso de uso para consultar los detalles de un usuario específico."""
from datetime import UTC, datetime

from app.application.dtos.user_dtos import UserResponse
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.exceptions.user import UserNotFoundError
from app.domain.value_objects import UserId


class GetUserUseCase:
    """Caso de uso para consultar los detalles de un usuario específico."""

    def __init__(self, uow: UnitOfWorkPort) -> None:  # noqa: D107
        self.uow = uow

    async def execute(self, user_id_str: str) -> UserResponse:
        """Busca un usuario por su ID único.

        Args:
            user_id_str: Identificador único del usuario.

        Returns:
            UserResponse con los datos del usuario encontrado.

        Raises:
            UserNotFoundError: Si no existe ningún usuario con el ID
                especificado.
        """
        user_id = UserId.from_string(user_id_str)

        async with self.uow:
            user = await self.uow.users.get_by_id(user_id)
            if not user:
                raise UserNotFoundError(
                    f"No se encontró ningún usuario con el ID "
                    f"'{user_id_str}'."
                )

            return UserResponse(
                id=str(user.id),
                email=user.email.value,
                nombre=user.nombre,
                empresa_id=str(user.empresa_id),
                telefono=user.telefono,
                activo=user.activo,
                created_at=user.created_at or datetime.now(UTC),
                updated_at=user.updated_at or datetime.now(UTC),
            )
