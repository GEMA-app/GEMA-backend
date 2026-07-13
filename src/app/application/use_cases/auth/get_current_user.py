"""Caso de uso para obtener los datos del usuario autenticado."""

from datetime import UTC, datetime

from app.application.dtos import GetCurrentUserRequest, UserResponse
from app.application.ports.auth import TokenServicePort
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.enums import CompanyStatus
from app.domain.exceptions import InvalidTokenError, UserInactiveError
from app.domain.value_objects import UserId


class GetCurrentUserUseCase:
    """Caso de uso para consultar la información del usuario autenticado actual."""

    def __init__(self, uow: UnitOfWorkPort, token_service: TokenServicePort) -> None:
        self.uow = uow
        self.token_service = token_service

    async def execute(self, request: GetCurrentUserRequest) -> UserResponse:
        """Decodifica el token de acceso, valida el estado del usuario y su empresa.

        Devuelve su perfil.
        """
        claims = await self.token_service.decode_token(request.access_token)

        if claims.get("type") != "access":
            raise InvalidTokenError("Se requiere un token de acceso válido para esta operación.")

        sub = claims["sub"]

        async with self.uow:
            user = await self.uow.users.get_by_id(UserId.from_string(sub))
            if not user or not user.activo:
                raise UserInactiveError("El usuario no existe o se encuentra inactivo.")

            company = await self.uow.companies.get_by_id(user.empresa_id)
            if company and company.estado != CompanyStatus.ACTIVE:
                raise UserInactiveError("La empresa se encuentra suspendida o cancelada.")

            roles_list: list[str] = []
            try:
                roles = await self.uow.roles.get_user_roles(user.id, user.empresa_id)
                roles_list = [r.nombre for r in roles]
            except Exception:
                roles_list = []

            created_at = user.created_at or datetime.now(UTC)
            updated_at = user.updated_at or datetime.now(UTC)

            return UserResponse(
                id=str(user.id),
                email=user.email.value,
                nombre=user.nombre,
                empresa_id=str(user.empresa_id),
                telefono=user.telefono,
                activo=user.activo,
                roles=roles_list,
                created_at=created_at,
                updated_at=updated_at,
            )
