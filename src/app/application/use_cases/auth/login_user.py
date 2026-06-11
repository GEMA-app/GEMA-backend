from app.application.dtos import AuthTokensDTO, LoginUserRequest
from app.application.ports.auth import PasswordHasherPort, TokenServicePort
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.enums import CompanyStatus
from app.domain.exceptions import InvalidCredentialsError, UserInactiveError
from app.domain.value_objects import Email

# Hash bcrypt real de 60 caracteres generado con bcrypt.hashpw(b"dummy", bcrypt.gensalt(12)).
# Garantiza timing constante cuando el email no existe, evitando enumeracion de usuarios
# por diferencia de tiempo (~95ms) entre usuario existente e inexistente.
_FAKE_HASH = "$2b$12$LpytE/S8f9VlE88I3G4CbeP8.p9XyD6s0V8rX3Y8g4d.qD6U5S1eO"
assert len(_FAKE_HASH) == 60, f"_FAKE_HASH debe tener 60 caracteres, tiene {len(_FAKE_HASH)}"


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
            stored_hash = user.password_hash.value if user else _FAKE_HASH

            if not self.hasher.verify(request.password, stored_hash):
                raise InvalidCredentialsError("Credenciales inválidas.")

            if not user:
                raise InvalidCredentialsError("Credenciales inválidas.")

            company = await self.uow.companies.get_by_id(user.empresa_id)
            if company and company.estado != CompanyStatus.ACTIVE:
                raise UserInactiveError("La empresa se encuentra suspendida o cancelada.")

            user.login()
            await self.uow.users.save(user)
            await self.uow.commit()

            access_token = await self.token_service.generate_access_token(str(user.id))
            refresh_token = await self.token_service.generate_refresh_token(str(user.id))

            return AuthTokensDTO(access_token=access_token, refresh_token=refresh_token)
