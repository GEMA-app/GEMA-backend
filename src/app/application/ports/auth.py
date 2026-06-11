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

    async def store_reset_token(
        self, token_hash: str, user_id: str, ttl_seconds: int
    ) -> None:
        """Almacena el hash de un token de reset de contraseña en Redis con TTL."""
        ...

    async def verify_reset_token(self, token_hash: str) -> str | None:
        """Devuelve el user_id asociado al token si es válido, None si no."""
        ...

    async def consume_reset_token(self, token_hash: str) -> str | None:
        """Obtiene y elimina el token de reset de forma atómica (GETDEL)."""
        ...

    async def delete_reset_token(self, token_hash: str) -> None:
        """Elimina un token de reset de contraseña (single-use)."""
        ...

    async def delete_user_reset_tokens(self, user_id: str) -> None:
        """Invalida todos los tokens de reset activos para un usuario."""
        ...

    async def claim_token(self, jti: str, exp: int) -> bool:
        """Intenta reclamar un token de forma atómica en Redis con un SET NX y TTL de 10s.
        Devuelve True si el token fue reclamado con éxito, False si ya existía.
        """
        ...
