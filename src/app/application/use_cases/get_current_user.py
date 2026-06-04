from app.application.dtos import UserResponse
from app.application.ports.auth import TokenServicePort
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.exceptions import InvalidTokenError, UserInactiveError
from app.domain.value_objects import UserId


class GetCurrentUserUseCase:
    """Caso de uso para consultar la información del usuario autenticado actual."""

    def __init__(self, uow: UnitOfWorkPort, token_service: TokenServicePort) -> None:
        self.uow = uow
        self.token_service = token_service

    async def execute(self, access_token: str) -> UserResponse:
        """Decodifica el token de acceso, valida el estado del usuario y devuelve su perfil."""
        claims = await self.token_service.decode_token(access_token)
        
        if claims.get("type") != "access":
            raise InvalidTokenError("Se requiere un token de acceso válido para esta operación.")

        sub = claims["sub"]

        async with self.uow:
            user = await self.uow.users.get_by_id(UserId.from_string(sub))
            if not user or not user.is_active:
                raise UserInactiveError("El usuario no existe o se encuentra inactivo.")

            return UserResponse(
                id=str(user.id),
                email=user.email.value,
                nombre=user.nombre,
                empresa_id=str(user.empresa_id),
                telefono=user.telefono,
                is_active=user.is_active,
                created_at=user.created_at,
                updated_at=user.updated_at,
            )
