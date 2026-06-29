"""Cliente Redis asíncrono con inicialización lazy y soporte para scripts Lua."""

from typing import Any, cast

import redis.asyncio as aioredis

from app.infrastructure.config.settings import settings


class _LazyScript:
    """Wrapper lazy para scripts Lua registrados en Redis.

    La conexión Redis se establece en la primera ejecución del script,
    no al registrarlo.
    """

    def __init__(self, script_text: str, client_ref: "RedisClient") -> None:
        self._script_text = script_text
        self._client_ref = client_ref
        self._real_script: Any = None

    async def __call__(self, keys: list[str] | None = None, args: list[str] | None = None) -> Any:
        if self._real_script is None:
            client = await self._client_ref._ensure_connected()
            self._real_script = client.register_script(self._script_text)
        return await self._real_script(keys=keys, args=args)

    def __repr__(self) -> str:
        return f"<LazyScript {self._script_text[:40]}...>"


class RedisClient:
    """Cliente Redis con inicialización lazy que actúa como proxy transparente.

    Los atributos/métodos que no existen en RedisClient se reenvían
    automáticamente al cliente ``aioredis.Redis`` subyacente.
    La conexión se establece bajo demanda (lazy).
    """

    def __init__(self) -> None:
        self._client: aioredis.Redis | None = None

    async def _ensure_connected(self) -> aioredis.Redis:
        """Establece la conexión Redis si aún no se ha hecho."""
        if self._client is None:
            self._client = cast(aioredis.Redis, cast(Any, aioredis).from_url(
                settings.REDIS_URL,
                decode_responses=True,
            ))
        return self._client

    def register_script(self, script: str) -> _LazyScript:
        """Registra un script Lua para ejecución posterior (lazy connect).

        Args:
            script: El texto del script Lua.

        Returns:
            Un objeto _LazyScript que cargará y ejecutará el script cuando sea invocado.
        """
        return _LazyScript(script, self)

    def __getattr__(self, name: str) -> Any:
        """Reenvía atributos no encontrados al cliente Redis subyacente.

        Args:
            name: Nombre del atributo a reenviar.

        Returns:
            Una coroutine function que conecta Redis bajo demanda.
        """

        async def _proxy(*args: Any, **kwargs: Any) -> Any:
            client = await self._ensure_connected()
            method = getattr(client, name)
            return await method(*args, **kwargs)

        return _proxy

    async def get_client(self) -> aioredis.Redis:
        """Devuelve la instancia del cliente Redis, conectando si es necesario.

        Returns:
            La instancia de aioredis.Redis conectada.
        """
        return await self._ensure_connected()

    async def close(self) -> None:
        """Cierra la conexión Redis si está abierta."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None


# Instancia singleton del cliente Redis lazy
redis_client = RedisClient()


async def get_redis() -> aioredis.Redis:
    """Devuelve la instancia del cliente asíncrono de Redis (lazy connect).

    Returns:
        El cliente asíncrono de Redis.
    """
    return await redis_client.get_client()
