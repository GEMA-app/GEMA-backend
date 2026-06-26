import hashlib
import secrets

import structlog

from app.application.dtos import RequestPasswordResetRequest
from app.application.ports.auth import TokenServicePort
from app.application.ports.notifications import NotificationPort
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.exceptions import InvalidEmailError
from app.domain.value_objects import Email

logger = structlog.get_logger()

_RESET_TOKEN_TTL_SECONDS = 1800
_RESET_TOKEN_EXPIRE_MINUTES = 30


class RequestPasswordResetUseCase:
    """Solicita un reset de contraseña enviando un email con un enlace de un solo uso."""

    def __init__(
        self,
        uow: UnitOfWorkPort,
        token_service: TokenServicePort,
        notification: NotificationPort,
        frontend_url: str,
    ) -> None:
        self.uow = uow
        self.token_service = token_service
        self.notification = notification
        self.frontend_url = frontend_url

    async def execute(self, request: RequestPasswordResetRequest) -> None:
        """Genera un token de reset y envía el email. Siempre retorna en silencio.

        Esto evita la enumeración de cuentas: ni un email inválido ni una cuenta
        inexistente producen una respuesta distinguible.
        """
        try:
            email = Email(value=request.email)
        except InvalidEmailError:
            return

        async with self.uow:
            user = await self.uow.users.get_by_email(email)
            if not user:
                return

            # Evento solo para auditoría, sin el token.
            user.request_password_reset()
            await self.uow.users.save(user)
            await self.uow.commit()

        # Invalidar tokens anteriores del mismo usuario (S-02: máximo 1 token activo).
        await self.token_service.delete_user_reset_tokens(str(user.id))

        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        await self.token_service.store_reset_token(
            token_hash=token_hash,
            user_id=str(user.id),
            ttl_seconds=_RESET_TOKEN_TTL_SECONDS,
        )

        # El email se envía directamente desde el use case para que el raw_token
        # nunca toque el bus de eventos ni la tabla outbox.
        await self.notification.send_password_reset(
            email=user.email.value,
            reset_url=f"{self.frontend_url}/reset-password?token={raw_token}",
            expire_minutes=_RESET_TOKEN_EXPIRE_MINUTES,
        )

        logger.info("password_reset_requested", user_id=str(user.id))
