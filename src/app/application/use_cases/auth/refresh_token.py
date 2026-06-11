import structlog

from app.application.dtos import AuthTokensDTO, RefreshTokenRequest
from app.application.ports.auth import TokenServicePort
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.enums import CompanyStatus
from app.domain.exceptions import InvalidTokenError, UserInactiveError
from app.domain.value_objects import UserId

logger = structlog.get_logger()


class RefreshTokenUseCase:
    """Rota los tokens de sesión de un usuario."""

    def __init__(self, uow: UnitOfWorkPort, token_service: TokenServicePort) -> None:
        """Guarda dependencias."""
        self.uow = uow
        self.token_service = token_service

    async def execute(self, request: RefreshTokenRequest) -> AuthTokensDTO:
        """Genera un nuevo par de tokens tras validar el token de refresco y prevenir ataques replay."""
        claims = await self.token_service.decode_token(request.refresh_token)

        if claims.get("type") != "refresh":
            raise InvalidTokenError("El token proporcionado no es un token de refresco válido.")

        jti = claims["jti"]
        exp = claims["exp"]
        sub = claims["sub"]

        # 1. Claim atómico vía TokenServicePort (SET NX encapsulado)
        # Safety net: TTL auto-expirado de 10s. Si Redis falla, fail-open controlado.
        try:
            if not await self.token_service.claim_token(jti=jti, exp=exp):
                raise InvalidTokenError("Token de refresco ya fue utilizado.")
        except InvalidTokenError:
            raise
        except Exception as e:
            logger.error("redis_unavailable_claim_token", error=str(e))
            # Fail-open: permitir refresh sin claim (menos seguro que lockout total)

        # 2. Transacción DB — SOLO lectura+escritura, sin side-effects Redis/JWT
        try:
            async with self.uow:
                user = await self.uow.users.get_by_id(UserId.from_string(sub))
                if not user or not user.activo:
                    raise UserInactiveError("El usuario no existe o se encuentra inactivo.")

                company = await self.uow.companies.get_by_id(user.empresa_id)
                if company and company.estado != CompanyStatus.ACTIVE:
                    raise UserInactiveError("La empresa se encuentra suspendida o cancelada.")
        except Exception:
            # Si DB falla, claim_token se auto-expira en 10s → sin daño permanente
            raise

        # 3. Side-effects Redis/JWT SOLO después de commit exitoso
        access_token = await self.token_service.generate_access_token(str(user.id))
        refresh_token = await self.token_service.generate_refresh_token(str(user.id))

        await self.token_service.revoke_token(jti=jti, exp=exp)

        return AuthTokensDTO(access_token=access_token, refresh_token=refresh_token)
