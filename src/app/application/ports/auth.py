from typing import Any, Protocol


class PasswordHasherPort(Protocol):
    """Puerto para el servicio de hashing y verificación de contraseñas."""

    def hash(self, password: str) -> str:
        """Genera un hash seguro a partir de una contraseña en texto plano."""
        ...

    def verify(self, password: str, hashed_password: str) -> bool:
        """Verifica que una contraseña plana coincida con un hash existente."""
        ...


class TokenServicePort(Protocol):
    """Puerto para el servicio de generación, validación y revocación de tokens JWT."""

    async def generate_access_token(self, subject: str) -> str:
        """Genera un token de acceso de corta duración para un sujeto (User ID)."""
        ...

    async def generate_refresh_token(self, subject: str) -> str:
        """Genera un token de refresco de larga duración para un sujeto (User ID)."""
        ...

    async def decode_token(self, token: str) -> dict[str, Any]:
        """Decodifica y valida un token JWT, devolviendo sus claims."""
        ...

    async def revoke_token(self, jti: str, exp: int) -> None:
        """Revoca un token identificándolo por su JTI e indicando su fecha de expiración."""
        ...
