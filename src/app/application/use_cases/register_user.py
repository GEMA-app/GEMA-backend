from app.application.dtos import AuthTokensDTO, RegisterUserRequest
from app.application.ports.auth import PasswordHasherPort, TokenServicePort
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.entities import User
from app.domain.exceptions import UserAlreadyExistsError
from app.domain.value_objects import Email, HashedPassword, PlainPassword


class RegisterUserUseCase:
    """Caso de uso para registrar un nuevo usuario en el sistema y generar sus tokens iniciales."""

    def __init__(
        self,
        uow: UnitOfWorkPort,
        hasher: PasswordHasherPort,
        token_service: TokenServicePort,
    ) -> None:
        self.uow = uow
        self.hasher = hasher
        self.token_service = token_service

    async def execute(self, request: RegisterUserRequest) -> AuthTokensDTO:
        """Ejecuta el flujo de registro, persistiendo transaccionalmente y emitiendo tokens JWT."""
        email = Email(value=request.email)
        plain_password = PlainPassword(value=request.password)

        async with self.uow:
            existing_user = await self.uow.users.get_by_email(email)
            if existing_user:
                raise UserAlreadyExistsError(
                    f"El correo electrónico '{request.email}' ya está registrado."
                )

            hashed_val = self.hasher.hash(plain_password.value)
            hashed_password = HashedPassword(value=hashed_val)

            user = User.register(email=email, hashed_password=hashed_password)
            await self.uow.users.save(user)
            await self.uow.commit()

            access_token = await self.token_service.generate_access_token(str(user.id))
            refresh_token = await self.token_service.generate_refresh_token(str(user.id))

            return AuthTokensDTO(access_token=access_token, refresh_token=refresh_token)
