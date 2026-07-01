"""Caso de uso para registrar un nuevo usuario (onboarding SaaS)."""

import asyncio

from app.application.dtos import AuthTokensDTO, RegisterUserRequest
from app.application.ports.auth import PasswordHasherPort, TokenServicePort
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.entities import Company, Role, User, UserPreference
from app.domain.exceptions import CompanySlugExistsError, UserAlreadyExistsError
from app.domain.value_objects import Email, HashedPassword, PlainPassword, Slug


class RegisterUserUseCase:
    """Registra un nuevo usuario en el sistema creando empresa y rol administrador."""

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
        """Ejecuta el flujo de registro (onboarding SaaS) y genera los tokens iniciales."""
        email = Email(value=request.email)
        plain_password = PlainPassword(value=request.password)
        hashed_val = await asyncio.to_thread(self.hasher.hash, plain_password.value)
        hashed_password = HashedPassword(value=hashed_val)

        async with self.uow:
            # 1. Verificar si el email ya está registrado globalmente
            existing_user = await self.uow.users.get_by_email(email)
            if existing_user:
                raise UserAlreadyExistsError(
                    f"El correo electrónico '{request.email}' ya está registrado."
                )

            # 2. Generar slug a partir del nombre de la empresa
            slug = Slug.from_name(request.company_name)
            existing_company = await self.uow.companies.get_by_slug(slug)
            if existing_company:
                raise CompanySlugExistsError(
                    f"El slug '{slug.value}' generado para la empresa ya existe."
                )

            # 3. Crear empresa
            company = Company.create(
                nombre=request.company_name, slug=slug, email_contacto=request.email
            )
            await self.uow.companies.save(company)

            # 4. Crear usuario vinculado a la nueva empresa
            user = User.register(
                email=email,
                password_hash=hashed_password,
                empresa_id=company.id,
                nombre=request.nombre,
                telefono=request.telefono,
                company_name=company.nombre,
            )
            await self.uow.users.save(user)

            # 5. Crear rol Administrador por defecto con todos los permisos
            admin_role = Role.create_admin(empresa_id=company.id)
            admin_role.record_assignment(user.id)
            await self.uow.roles.save(admin_role)

            # 6. Asignar el rol al usuario creado
            await self.uow.roles.assign_to_user(admin_role.id, user.id)

            # 7. Crear preferencias por defecto (evita 404 en GET /preferences)
            prefs = UserPreference.create(
                usuario_id=user.id,
                empresa_id=company.id,
            )
            await self.uow.preferences.save(prefs)

            await self.uow.commit()

            # Generar tokens
            access_token = await self.token_service.generate_access_token(str(user.id))
            refresh_token = await self.token_service.generate_refresh_token(str(user.id))

            return AuthTokensDTO(access_token=access_token, refresh_token=refresh_token)
