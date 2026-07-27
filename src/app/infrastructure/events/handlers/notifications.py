"""Handlers de eventos de dominio que despachan notificaciones por correo."""

import uuid

import structlog

from app.application.ports.notifications import NotificationPort
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.entities.system_audit import SystemAudit
from app.domain.events import (
    PasswordChanged,
    PasswordResetCompleted,
    PasswordResetInitiated,
    UserLoggedIn,
    UserRegistered,
)
from app.domain.value_objects import CompanyId, UserId

logger = structlog.get_logger()


async def handle_user_registered(
    event: UserRegistered,
    notification: NotificationPort,
) -> None:
    """Despacha el email de bienvenida al usuario recién registrado.

    Args:
        event: Evento de dominio con datos del usuario registrado.
        notification: Puerto de notificaciones para enviar el correo.
    """
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
    uow: UnitOfWorkPort | None = None,
) -> None:
    """Envía la alerta de seguridad cuando la contraseña ha sido cambiada.

    Args:
        event: Evento de dominio con datos del cambio de contraseña.
        notification: Puerto de notificaciones para enviar el correo.
        uow: Unit of Work opcional para persistir auditoría.
    """
    logger.info("handle_password_changed", user_id=event.user_id)
    await notification.send_password_changed(email=event.email)
    if uow and event.empresa_id and event.user_id:
        try:
            audit = SystemAudit.create(
                empresa_id=CompanyId(value=uuid.UUID(event.empresa_id)),
                usuario_id=UserId(value=uuid.UUID(event.user_id)),
                accion="cambio_contrasena",
                detalles={"email": event.email},
            )
            async with uow:
                await uow.system_audits.save(audit)
                await uow.commit()
        except Exception as err:
            logger.warning("audit_log_failed", error=str(err))


async def handle_password_reset_initiated(
    event: PasswordResetInitiated,
    notification: NotificationPort,
) -> None:
    """Handler de auditoría — el email ya fue enviado desde el use case.

    Args:
        event: Evento de dominio con datos del restablecimiento.
        notification: Puerto de notificaciones (no se envía correo aquí).
    """
    logger.info(
        "handle_password_reset_initiated",
        user_id=event.user_id,
        email=event.email,
        msg="Email de reset enviado desde el use case (raw_token nunca persiste)",
    )


async def handle_password_reset_completed(
    event: PasswordResetCompleted,
    notification: NotificationPort,
    uow: UnitOfWorkPort | None = None,
) -> None:
    """Envía la confirmación de que la contraseña fue restablecida.

    Args:
        event: Evento de dominio con datos del restablecimiento completado.
        notification: Puerto de notificaciones para enviar el correo.
        uow: Unit of Work opcional para auditoría.
    """
    logger.info("handle_password_reset_completed", user_id=event.user_id)
    await notification.send_password_reset_confirmation(email=event.email)
    if uow and event.empresa_id and event.user_id:
        try:
            audit = SystemAudit.create(
                empresa_id=CompanyId(value=uuid.UUID(event.empresa_id)),
                usuario_id=UserId(value=uuid.UUID(event.user_id)),
                accion="restablecimiento_contrasena",
                detalles={"email": event.email},
            )
            async with uow:
                await uow.system_audits.save(audit)
                await uow.commit()
        except Exception as err:
            logger.warning("audit_log_failed", error=str(err))


async def handle_user_logged_in(
    event: UserLoggedIn,
    uow: UnitOfWorkPort,
) -> None:
    """Registra el inicio de sesión en la tabla de auditoría.

    Args:
        event: Evento de dominio con datos del usuario que inició sesión.
        uow: Unit of Work para persistir el registro de auditoría.
    """
    logger.info("handle_user_logged_in", user_id=event.user_id, email=event.email)

    audit = SystemAudit.create(
        empresa_id=CompanyId(value=uuid.UUID(event.empresa_id)),
        usuario_id=UserId(value=uuid.UUID(event.user_id)),
        accion="inicio_sesion",
        detalles={"email": event.email},
    )

    async with uow:
        await uow.system_audits.save(audit)
        await uow.commit()
