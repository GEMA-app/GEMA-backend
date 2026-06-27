"""Caso de uso para actualización parcial de usuarios."""

from datetime import UTC, datetime

from app.application.dtos.user_dtos import UpdateUserRequest, UserResponse
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.exceptions.user import UserNotFoundError
from app.domain.value_objects import Email, UserId


class EditUserUseCase:
    """Caso de uso para actualizar parcialmente los datos de un usuario."""

    def __init__(self, uow: UnitOfWorkPort) -> None:  # noqa: D107
        self.uow = uow

    async def execute(
        self, user_id_str: str, request: UpdateUserRequest
    ) -> UserResponse:
        """Actualiza los campos enviados de un usuario existente.

        Args:
            user_id_str: Identificador único del usuario.
            request: DTO con los campos a actualizar (todos opcionales).

        Returns:
            UserResponse con los datos del usuario actualizado.

        Raises:
            UserNotFoundError: Si no existe un usuario con el ID especificado.
        """
        user_id = UserId.from_string(user_id_str)

        async with self.uow:
            user = await self.uow.users.get_by_id(user_id)
            if not user:
                raise UserNotFoundError(
                    f"No se encontró ningún usuario con el ID "
                    f"'{user_id_str}'."
                )

            if request.nombre is not None:
                user.nombre = request.nombre
            if request.email is not None:
                user.email = Email(value=request.email)
            if request.telefono is not None:
                user.telefono = request.telefono
            if request.activo is not None:
                if request.activo:
                    user.activate()
                else:
                    user.deactivate()

            await self.uow.users.save(user)
            await self.uow.commit()

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
