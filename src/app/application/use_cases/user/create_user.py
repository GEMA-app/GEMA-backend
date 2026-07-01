"""Caso de uso para registrar un nuevo usuario dentro de una empresa."""

import asyncio
from datetime import UTC, datetime

from app.application.dtos.user_dtos import CreateUserRequest, UserResponse
from app.application.ports.auth import PasswordHasherPort
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.entities.user import User
from app.domain.exceptions import UserAlreadyExistsError
from app.domain.value_objects import CompanyId, Email, HashedPassword


class CreateUserUseCase:
    """Caso de uso para registrar un nuevo usuario dentro de una empresa."""

    def __init__(self, uow: UnitOfWorkPort, hasher: PasswordHasherPort) -> None:  # noqa: D107
        self.uow = uow
        self.hasher = hasher

    async def execute(self, company_id_str: str, request: CreateUserRequest) -> UserResponse:
        """Registra un nuevo usuario aplicando las reglas de la arquitectura.

        Args:
            company_id_str: Identificador de la empresa (tenant).
            request: DTO con los datos del usuario a crear.

        Returns:
            UserResponse con los datos del usuario registrado.

        Raises:
            UserAlreadyExistsError: Si ya existe un usuario con el correo
                electrónico especificado en la base de datos.
        """
        company_id = CompanyId.from_string(company_id_str)
        email_vo = Email(value=request.email)

        async with self.uow:
            existing_user = await self.uow.users.get_by_email(email_vo)
            if existing_user:
                raise UserAlreadyExistsError(
                    f"Ya existe un usuario registrado con el correo '{request.email}'."
                )

            hashed_val = await asyncio.to_thread(self.hasher.hash, request.password)
            password_hash = HashedPassword(value=hashed_val)

            user = User.register(
                email=email_vo,
                password_hash=password_hash,
                empresa_id=company_id,
                nombre=request.nombre,
                telefono=request.telefono,
            )

            await self.uow.users.save(user)
            await self.uow.commit()

            return UserResponse(
                id=str(user.id),
                email=user.email.value,
                nombre=user.nombre,
                empresa_id=str(user.empresa_id),
                telefono=user.telefono,
                activo=user.activo,
                created_at=user.created_at or datetime.now(UTC),
                updated_at=user.updated_at or datetime.now(UTC),
                roles=[r.nombre for r in user.roles],
            )
