from app.application.dtos import AuthTokensDTO, RefreshTokenRequest
from app.application.ports.auth import TokenServicePort
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.exceptions import InvalidTokenError, UserInactiveError
from app.domain.value_objects import UserId


class RefreshTokenUseCase:
    """Caso de uso para rotar tokens de refresco, emitiendo un nuevo par y revocando el anterior."""

    def __init__(self, uow: UnitOfWorkPort, token_service: TokenServicePort) -> None:
        """Inicializa el caso de uso con la unidad de trabajo (UoW) y el servicio de tokens."""
        self.uow = uow
        self.token_service = token_service

    async def execute(self, request: RefreshTokenRequest) -> AuthTokensDTO:
        """Valida y revoca el token de refresco actual, generando uno nuevo para el usuario."""
        claims = await self.token_service.decode_token(request.refresh_token)

        if claims.get("type") != "refresh":
            raise InvalidTokenError("El token proporcionado no es un token de refresco válido.")

        jti = claims["jti"]
        exp = claims["exp"]
        sub = claims["sub"]

        async with self.uow:
            user = await self.uow.users.get_by_id(UserId.from_string(sub))
            if not user or not user.is_active:
                raise UserInactiveError("El usuario no existe o se encuentra inactivo.")

            access_token = await self.token_service.generate_access_token(str(user.id))
            refresh_token = await self.token_service.generate_refresh_token(str(user.id))

        await self.token_service.revoke_token(jti=jti, exp=exp)

        return AuthTokensDTO(access_token=access_token, refresh_token=refresh_token)
