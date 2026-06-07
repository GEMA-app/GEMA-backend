from app.application.dtos import AuthTokensDTO, LoginUserRequest
from app.application.ports.auth import PasswordHasherPort, TokenServicePort
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.exceptions import InvalidCredentialsError
from app.domain.value_objects import Email


class LoginUserUseCase:
    """Caso de uso para autenticar un usuario y generar sus tokens de acceso."""

    def __init__(
        self,
        uow: UnitOfWorkPort,
        hasher: PasswordHasherPort,
        token_service: TokenServicePort,
    ) -> None:
        self.uow = uow
        self.hasher = hasher
        self.token_service = token_service

    async def execute(self, request: LoginUserRequest) -> AuthTokensDTO:
        """Valida credenciales, registra el inicio de sesión y emite el par de tokens JWT."""
        email = Email(value=request.email)

        async with self.uow:
            user = await self.uow.users.get_by_email(email)
            if not user:
                raise InvalidCredentialsError("Credenciales inválidas.")

            if not self.hasher.verify(request.password, user.password_hash.value):
                raise InvalidCredentialsError("Credenciales inválidas.")

            user.login()
            await self.uow.users.save(user)
            await self.uow.commit()

            access_token = await self.token_service.generate_access_token(str(user.id))
            refresh_token = await self.token_service.generate_refresh_token(str(user.id))

            return AuthTokensDTO(access_token=access_token, refresh_token=refresh_token)
