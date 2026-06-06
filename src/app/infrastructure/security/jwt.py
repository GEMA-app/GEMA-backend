import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from redis.asyncio import Redis

from app.application.ports.auth import TokenServicePort
from app.domain.exceptions import InvalidTokenError
from app.infrastructure.config.settings import settings


class PyJwtTokenService(TokenServicePort):
    """Implementación de TokenServicePort utilizando PyJWT y Redis para la lista de bloqueo."""

    def __init__(self, redis_client: Redis) -> None:
        self.redis = redis_client

    async def generate_access_token(self, subject: str) -> str:
        """Genera un token de acceso JWT con JTI único y tiempo de expiración corto."""
        now = datetime.now(UTC)
        expire = now + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {
            "sub": subject,
            "jti": str(uuid.uuid4()),
            "type": "access",
            "exp": int(expire.timestamp()),
            "iat": int(now.timestamp()),
        }
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    async def generate_refresh_token(self, subject: str) -> str:
        """Genera un token de refresco JWT con JTI único y tiempo de expiración largo."""
        now = datetime.now(UTC)
        expire = now + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
        payload = {
            "sub": subject,
            "jti": str(uuid.uuid4()),
            "type": "refresh",
            "exp": int(expire.timestamp()),
            "iat": int(now.timestamp()),
        }
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    async def decode_token(self, token: str) -> dict[str, Any]:
        """Decodifica un token JWT, valida sus claims y verifica que no esté revocado en Redis."""
        try:
            claims = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
                options={"require": ["exp", "sub", "jti"]},
            )
        except jwt.ExpiredSignatureError:
            raise InvalidTokenError("El token ha expirado.") from None
        except jwt.InvalidTokenError:
            raise InvalidTokenError("Token JWT inválido.") from None

        jti = claims["jti"]
        is_revoked = await self.redis.get(f"blocklist:{jti}")
        if is_revoked:
            raise InvalidTokenError("El token ha sido revocado.")

        return claims

    async def revoke_token(self, jti: str, exp: int) -> None:
        """Añade un JTI a la lista de bloqueo de Redis con un TTL igual al tiempo de vida restante."""
        now = int(datetime.now(UTC).timestamp())
        ttl = exp - now
        if ttl > 0:
            await self.redis.set(f"blocklist:{jti}", "revoked", ex=ttl)
