from app.application.ports.auth import TokenServicePort
from app.domain.exceptions import InvalidTokenError


class LogoutUserUseCase:
    """Caso de uso para cerrar sesión, revocando el token de acceso actual en la lista de bloqueo."""

    def __init__(self, token_service: TokenServicePort) -> None:
        self.token_service = token_service

    async def execute(self, access_token: str, refresh_token: str | None = None) -> None:
        """Decodifica el token de acceso y lo registra en la lista de bloqueo, revoca también el de refresco si se proporciona."""
        claims = await self.token_service.decode_token(access_token)

        if claims.get("type") != "access":
            raise InvalidTokenError(
                "Solo se pueden revocar tokens de acceso durante el cierre de sesión."
            )

        jti = claims["jti"]
        exp = claims["exp"]

        await self.token_service.revoke_token(jti=jti, exp=exp)

        if refresh_token:
            try:
                refresh_claims = await self.token_service.decode_token(refresh_token)
                if refresh_claims.get("type") == "refresh":
                    await self.token_service.revoke_token(
                        jti=refresh_claims["jti"], exp=refresh_claims["exp"]
                    )
            except InvalidTokenError:
                pass  # Si ya expiró, no pasa nada
