import contextlib
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any, cast

import jwt
from redis.asyncio import Redis

from app.application.ports.auth import TokenServicePort
from app.domain.exceptions import InvalidTokenError
from app.infrastructure.config.settings import settings

RESET_TOKEN_PREFIX = "gema:reset_token:"
RESET_TOKEN_USER_SET_PREFIX = "gema:user_reset_tokens:"


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

    async def store_reset_token(
        self, token_hash: str, user_id: str, ttl_seconds: int
    ) -> None:
        """Almacena el hash del token y registra el usuario en el set de tokens."""
        key = f"{RESET_TOKEN_PREFIX}{token_hash}"
        user_key = f"{RESET_TOKEN_USER_SET_PREFIX}{user_id}"
        async with self.redis.pipeline(transaction=True) as pipe:
            pipe.setex(key, ttl_seconds, user_id)
            pipe.sadd(user_key, token_hash)
            pipe.expire(user_key, ttl_seconds)
            await pipe.execute()

    async def verify_reset_token(self, token_hash: str) -> str | None:
        """Devuelve el user_id asociado al token si existe y no ha expirado."""
        key = f"{RESET_TOKEN_PREFIX}{token_hash}"
        result = await self.redis.get(key)
        return cast("str | None", result)

    async def consume_reset_token(self, token_hash: str) -> str | None:
        """GETDEL atómico: obtiene user_id Y elimina el token en una operación."""
        key = f"{RESET_TOKEN_PREFIX}{token_hash}"
        user_id = await self.redis.getdel(key)
        if user_id:
            user_id_str = cast(str, user_id)
            user_key = f"{RESET_TOKEN_USER_SET_PREFIX}{user_id_str}"
            with contextlib.suppress(Exception):
                res_srem = self.redis.srem(user_key, token_hash)
                if not isinstance(res_srem, int):
                    await res_srem
            return user_id_str
        return None

    async def delete_reset_token(self, token_hash: str) -> None:
        """Elimina el token y lo quita del set de tokens del usuario."""
        key = f"{RESET_TOKEN_PREFIX}{token_hash}"
        user_id = await self.redis.get(key)
        if user_id:
            user_key = f"{RESET_TOKEN_USER_SET_PREFIX}{cast(str, user_id)}"
            async with self.redis.pipeline(transaction=True) as pipe:
                pipe.delete(key)
                pipe.srem(user_key, token_hash)
                await pipe.execute()

    async def delete_user_reset_tokens(self, user_id: str) -> None:
        """Invalida todos los tokens de reset activos de un usuario."""
        user_key = f"{RESET_TOKEN_USER_SET_PREFIX}{user_id}"
        res_smembers = self.redis.smembers(user_key)
        if not isinstance(res_smembers, set):
            token_hashes = await res_smembers
        else:
            token_hashes = res_smembers
        if token_hashes:
            keys = [f"{RESET_TOKEN_PREFIX}{cast(str, th)}" for th in token_hashes]
            async with self.redis.pipeline(transaction=True) as pipe:
                pipe.delete(*keys)
                pipe.delete(user_key)
                await pipe.execute()

    async def claim_token(self, jti: str, exp: int) -> bool:
        """Intenta reclamar un token de forma atómica en Redis con un SET NX y TTL de 10s."""
        key = f"claim:{jti}"
        result = await self.redis.set(key, "claimed", ex=10, nx=True)
        return bool(result)
