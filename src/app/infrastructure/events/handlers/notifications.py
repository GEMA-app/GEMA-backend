import structlog

from app.application.ports.notifications import NotificationPort
from app.domain.events import (
    PasswordChanged,
    PasswordResetCompleted,
    PasswordResetInitiated,
    UserRegistered,
)

logger = structlog.get_logger()


async def handle_user_registered(
    event: UserRegistered,
    notification: NotificationPort,
) -> None:
    """Despacha el email de bienvenida al usuario recién registrado."""
    logger.info(
        "handle_user_registered",
        user_id=event.user_id,
        email=event.email,
    )
    await notification.send_welcome(
        email=event.email,
        nombre=event.nombre or event.email.split("@")[0],
        company_name=event.company_name or "tu empresa",
    )


async def handle_password_changed(
    event: PasswordChanged,
    notification: NotificationPort,
) -> None:
    """Envía la alerta de seguridad cuando la contraseña ha sido cambiada."""
    logger.info("handle_password_changed", user_id=event.user_id)
    await notification.send_password_changed(email=event.email)


async def handle_password_reset_initiated(
    event: PasswordResetInitiated,
    notification: NotificationPort,
) -> None:
    """Handler de auditoría — el email ya fue enviado desde el use case."""
    logger.info(
        "handle_password_reset_initiated",
        user_id=event.user_id,
        email=event.email,
        msg="Email de reset enviado desde el use case (raw_token nunca persiste)",
    )


async def handle_password_reset_completed(
    event: PasswordResetCompleted,
    notification: NotificationPort,
) -> None:
    """Envía la confirmación de que la contraseña fue restablecida."""
    logger.info("handle_password_reset_completed", user_id=event.user_id)
    await notification.send_password_reset_confirmation(email=event.email)
