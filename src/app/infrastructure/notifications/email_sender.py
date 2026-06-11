import smtplib
import time
from email.mime.text import MIMEText
from pathlib import Path
from string import Template

import anyio
import structlog

from app.application.ports.notifications import NotificationPort
from app.infrastructure.config.settings import settings

logger = structlog.get_logger()


class NotificationError(Exception):
    """Excepción base para errores del servicio de notificaciones."""


class TemplateNotFoundError(NotificationError):
    """Se lanza cuando se solicita un template que no existe."""


class SmtpNotificationSender(NotificationPort):
    """Adaptador SMTP construido sobre la librería estándar."""

    def __init__(self) -> None:
        self._templates_dir = Path(__file__).parent / "templates"
        self._cache: dict[str, Template] = {}

        for f in self._templates_dir.glob("*.html"):
            content = f.read_text(encoding="utf-8")
            self._cache[f.stem] = Template(content)

    def _render(self, template_name: str, **kwargs: str) -> str:
        template = self._cache.get(template_name)
        if not template:
            raise TemplateNotFoundError(f"Template no encontrado: {template_name}")
        return template.safe_substitute(**kwargs)

    async def send_welcome(self, email: str, nombre: str, company_name: str) -> None:
        """Envía el email de bienvenida al nuevo usuario."""
        body = self._render(
            "welcome", nombre=nombre, company_name=company_name
        )
        await self._send(email, "¡Bienvenido a GEMA!", body)

    async def send_password_changed(self, email: str) -> None:
        """Envía la alerta de seguridad por cambio de contraseña."""
        body = self._render("password_changed")
        await self._send(email, "Tu contraseña de GEMA ha sido cambiada", body)

    async def send_password_reset(
        self, email: str, reset_url: str, expire_minutes: int
    ) -> None:
        """Envía el email con el enlace para restablecer la contraseña."""
        body = self._render(
            "password_reset",
            reset_url=reset_url,
            expire_minutos=str(expire_minutes),
        )
        await self._send(email, "Restablece tu contraseña de GEMA", body)

    async def send_password_reset_confirmation(self, email: str) -> None:
        """Envía la confirmación del restablecimiento de contraseña."""
        body = self._render("password_reset_confirmed")
        await self._send(email, "Tu contraseña de GEMA ha sido restablecida", body)

    async def _send(self, to: str, subject: str, html_body: str) -> None:
        """Envía el email a través de SMTP o lo registra según el provider configurado."""
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
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=5) as server:
                if settings.SMTP_USE_TLS:
                    server.starttls()
                if settings.SMTP_USER and settings.SMTP_PASSWORD:
                    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
            elapsed = time.monotonic() - start
            logger.info("email_sent", to=to, elapsed_ms=round(elapsed * 1000))

        await anyio.to_thread.run_sync(_blocking_send)
