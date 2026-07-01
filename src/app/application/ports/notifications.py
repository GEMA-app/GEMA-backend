"""Puerto (Protocol) del servicio de notificaciones (NotificationPort)."""

from typing import Protocol


class NotificationPort(Protocol):
    """Puerto para enviar notificaciones transaccionales a usuarios."""

    async def send_welcome(self, email: str, nombre: str, company_name: str) -> None:
        """Envía el email de bienvenida a un nuevo usuario."""
        ...

    async def send_password_changed(self, email: str) -> None:
        """Envía la alerta de seguridad cuando la contraseña ha sido cambiada."""
        ...

    async def send_password_reset(self, email: str, reset_url: str, expire_minutes: int) -> None:
        """Envía el email con el enlace de restablecimiento de contraseña."""
        ...

    async def send_password_reset_confirmation(self, email: str) -> None:
        """Envía la confirmación de que la contraseña fue restablecida."""
        ...
