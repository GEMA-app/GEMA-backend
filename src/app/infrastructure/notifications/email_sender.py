"""Implementación concreta de NotificationPort para el envío de correos vía SMTP."""

import smtplib
import time
from email.mime.text import MIMEText
from string import Template

import anyio
import structlog

from app.application.ports.notifications import NotificationPort
from app.domain.exceptions import DomainException
from app.infrastructure.config.settings import settings

logger = structlog.get_logger()


class NotificationError(DomainException):
    """Excepción base para errores del servicio de notificaciones."""


class TemplateNotFoundError(DomainException):
    """Se lanza cuando se solicita un template que no existe."""


class SmtpNotificationSender(NotificationPort):
    """Adaptador SMTP construido sobre la librería estándar.

    Los templates se cargan de forma síncrona durante la inicialización.
    Nota: para entornos de alto rendimiento asíncrono, considerar migrar
    la carga de templates a startup con aiofiles o anyio.Path.
    """

    def __init__(self) -> None:
        """Inicializa el cargador de templates desde el directorio configurado."""
        self._templates_dir = settings.EMAIL_TEMPLATES_DIR
        self._cache: dict[str, Template] = {}

    async def _render(self, template_name: str, **kwargs: str) -> str:
        """Renderiza una plantilla aplicando sustitución de variables de forma asíncrona.

        Args:
            template_name: Nombre del archivo de plantilla (sin extensión).
            **kwargs: Variables a reemplazar en el template.

        Returns:
            El contenido HTML renderizado.

        Raises:
            TemplateNotFoundError: Si el template solicitado no existe en la caché ni en el disco.
        """
        template = self._cache.get(template_name)
        if not template:
            template_path = self._templates_dir / f"{template_name}.html"
            try:
                from anyio import Path
                path = Path(template_path)
                if await path.exists():
                    content = await path.read_text(encoding="utf-8")
                    template = Template(content)
                    self._cache[template_name] = template
            except Exception as e:
                logger.error(
                    "Error al cargar la plantilla de correo",
                    template=template_name,
                    error=str(e),
                )
        if not template:
            raise TemplateNotFoundError(f"Template no encontrado: {template_name}")
        return template.safe_substitute(**kwargs)

    async def send_welcome(self, email: str, nombre: str, company_name: str) -> None:
        """Envía el email de bienvenida al nuevo usuario.

        Args:
            email: Dirección de correo del destinatario.
            nombre: Nombre del usuario para personalizar el saludo.
            company_name: Nombre de la empresa para personalizar el contenido.

        Raises:
            TemplateNotFoundError: Si el template welcome no existe.
            NotificationError: Si falla el envío SMTP.
        """
        body = await self._render(
            "welcome", nombre=nombre, company_name=company_name
        )
        await self._send(email, "¡Bienvenido a GEMA!", body)

    async def send_password_changed(self, email: str) -> None:
        """Envía la alerta de seguridad por cambio de contraseña.

        Args:
            email: Dirección de correo del destinatario.

        Raises:
            TemplateNotFoundError: Si el template password_changed no existe.
            NotificationError: Si falla el envío SMTP.
        """
        body = await self._render("password_changed")
        await self._send(email, "Tu contraseña de GEMA ha sido cambiada", body)

    async def send_password_reset(
        self, email: str, reset_url: str, expire_minutes: int
    ) -> None:
        """Envía el email con el enlace para restablecer la contraseña.

        Args:
            email: Dirección de correo del destinatario.
            reset_url: URL completa para restablecer la contraseña.
            expire_minutes: Minutos de validez del enlace.

        Raises:
            TemplateNotFoundError: Si el template password_reset no existe.
            NotificationError: Si falla el envío SMTP.
        """
        body = await self._render(
            "password_reset",
            reset_url=reset_url,
            expire_minutes=str(expire_minutes),
        )
        await self._send(email, "Restablece tu contraseña de GEMA", body)

    async def send_password_reset_confirmation(self, email: str) -> None:
        """Envía la confirmación del restablecimiento de contraseña.

        Args:
            email: Dirección de correo del destinatario.

        Raises:
            TemplateNotFoundError: Si el template de confirmación no existe.
            NotificationError: Si falla el envío SMTP.
        """
        body = await self._render("password_reset_confirmed")
        await self._send(email, "Tu contraseña de GEMA ha sido restablecida", body)

    async def _send(self, to: str, subject: str, html_body: str) -> None:
        """Envía el email a través de SMTP o lo registra según el provider configurado.

        Args:
            to: Dirección de correo del destinatario.
            subject: Asunto del correo.
            html_body: Cuerpo del mensaje en formato HTML.

        Raises:
            NotificationError: Si el envío SMTP falla o hay error de conexión.
        """
        if settings.EMAIL_PROVIDER == "log":
            logger.info(
                "email_log_mode",
                to=to,
                subject=subject,
                body_length=len(html_body),
            )
            return

        def _blocking_send() -> None:
            msg = MIMEText(html_body, "html", "utf-8")
            msg["Subject"] = subject
            msg["From"] = (
                f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM_ADDRESS}>"
            )
            msg["To"] = to

            start = time.monotonic()
            try:
                with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=5) as server:
                    if settings.SMTP_USE_TLS:
                        server.starttls()
                    if settings.SMTP_USER and settings.SMTP_PASSWORD:
                        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                    server.send_message(msg)
            except (smtplib.SMTPException, OSError) as e:
                raise NotificationError(f"Error al enviar email SMTP: {e}") from e
            elapsed = time.monotonic() - start
            logger.info("email_sent", to=to, elapsed_ms=round(elapsed * 1000))

        await anyio.to_thread.run_sync(_blocking_send)
