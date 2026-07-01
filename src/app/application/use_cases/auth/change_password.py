"""Caso de uso para cambiar la contrasena del usuario autenticado."""
import asyncio
import uuid

import structlog

from app.application.dtos import ChangePasswordRequest
from app.application.ports.auth import PasswordHasherPort
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.exceptions import InvalidCredentialsError
from app.domain.value_objects import PlainPassword, UserId

logger = structlog.get_logger()


class ChangePasswordUseCase:
    """Caso de uso para que un usuario autenticado cambie su contraseña."""

    def __init__(
        self,
        uow: UnitOfWorkPort,
        hasher: PasswordHasherPort,
    ) -> None:
        self.uow = uow
        self.hasher = hasher

    async def execute(self, request: ChangePasswordRequest) -> None:
        """Valida la contraseña actual y emite PasswordChanged al reemplazarla."""
        validated = PlainPassword(value=request.new_password)
        new_hashed = await asyncio.to_thread(self.hasher.hash, validated.value)

        async with self.uow:
            user = await self.uow.users.get_by_id(UserId(value=uuid.UUID(request.user_id)))
            if not user:
                logger.warning("change_password_failed", user_id=request.user_id)
                raise InvalidCredentialsError("No se pudo cambiar la contraseña")

            is_valid = await asyncio.to_thread(
                self.hasher.verify, request.old_password, user.password_hash.value
            )
            if not is_valid:
                logger.warning("change_password_failed", user_id=request.user_id)
                raise InvalidCredentialsError("No se pudo cambiar la contraseña")

            user.change_password(new_hashed)
            await self.uow.users.save(user)
            await self.uow.commit()
