"""Puerto que define el contrato para el limitador de tasa (rate limiting)."""

from typing import Protocol


class RateLimiterPort(Protocol):
    """Interfaz abstracta para verificar y aplicar límites de tasa."""

    async def is_rate_limited(self, key: str, limit: int, window_seconds: int) -> bool:
        """Verifica si el número de solicitudes ha excedido el límite configurado.

        Args:
            key: Identificador único del recurso o cliente (ej. IP, email, endpoint).
            limit: Número máximo de solicitudes permitidas en la ventana de tiempo.
            window_seconds: Ventana de tiempo en segundos.

        Returns:
            True si se ha excedido el límite y debe denegarse la solicitud, False en caso contrario.
        """
        ...
