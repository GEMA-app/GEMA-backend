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

        user_id = await self.token_service.consume_reset_token(token_hash)
        if not user_id:
            logger.warning(
                "reset_token_fallido",
                motivo="token_invalido_o_expirado",
            )
            raise InvalidTokenError("Token inválido o expirado")

        validated = PlainPassword(value=new_password)
        import asyncio
        new_hashed = await asyncio.to_thread(self.hasher.hash, validated.value)

        try:
            async with self.uow:
                user = await self.uow.users.get_by_id(UserId(value=uuid.UUID(user_id)))
                if not user:
                    logger.error(
                        "reset_token_usuario_inexistente",
                        user_id=user_id,
                    )
                    raise InvalidTokenError("Token inválido o expirado")

                user.complete_password_reset(new_hashed)
                await self.uow.users.save(user)
                await self.uow.commit()
        except Exception as err:
            # Restaurar token si el commit/proceso falla (rollback automático de BD)
            # ⚠️ SIEMPRE propagar error original, incluso si Redis falla
            try:
                await self.token_service.store_reset_token(
                    token_hash, user_id, 1800
                )
            except Exception as cache_err:
                logger.error(
                    "Fallo al restaurar token en cache tras rollback de BD",
                    redis_error=str(cache_err),
                )
            raise err

        await self.notification.send_password_reset_confirmation(
            email=user.email.value,
        )
        logger.info("reset_password_completado", user_id=user_id)
