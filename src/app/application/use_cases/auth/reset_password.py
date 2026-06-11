import hashlib
import uuid

import structlog

from app.application.ports.auth import PasswordHasherPort, TokenServicePort
from app.application.ports.notifications import NotificationPort
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.exceptions import InvalidTokenError
from app.domain.value_objects import PlainPassword, UserId

logger = structlog.get_logger()


class ResetPasswordUseCase:
    """Completa un reset de contraseña validando el token de un solo uso."""

    def __init__(
        self,
        uow: UnitOfWorkPort,
        hasher: PasswordHasherPort,
        token_service: TokenServicePort,
        notification: NotificationPort,
    ) -> None:
        self.uow = uow
        self.hasher = hasher
        self.token_service = token_service
        self.notification = notification

    async def execute(self, raw_token: str, new_password: str) -> None:
        """Valida el token, actualiza la contraseña y elimina el token."""
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()

        user_id = await self.token_service.verify_reset_token(token_hash)
        if not user_id:
            logger.warning(
                "reset_token_fallido",
                motivo="token_invalido_o_expirado",
            )
            raise InvalidTokenError("Token inválido o expirado")

        async with self.uow:
            user = await self.uow.users.get_by_id(UserId(value=uuid.UUID(user_id)))
            if not user:
                logger.error(
                    "reset_token_usuario_inexistente",
                    user_id=user_id,
                )
                raise InvalidTokenError("Token inválido o expirado")

            validated = PlainPassword(value=new_password)
            user.complete_password_reset(self.hasher.hash(validated.value))
            await self.uow.users.save(user)

            # Eliminar el token dentro de la misma transacción que el cambio de contraseña.
            # Si Redis falla, el commit se revierte y la contraseña no cambia.
            await self.token_service.delete_reset_token(token_hash)

            await self.uow.commit()

            await self.notification.send_password_reset_confirmation(
                email=user.email.value,
            )
            logger.info("reset_password_completado", user_id=user_id)
