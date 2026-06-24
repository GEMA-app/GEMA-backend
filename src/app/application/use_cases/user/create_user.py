from app.application.dtos.user_dtos import CreateUserRequest, UserResponse
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.entities.user import User
from app.domain.exceptions.auth import UserAlreadyExistsError
from app.domain.value_objects import CompanyId, Email, HashedPassword


class CreateUserUseCase:
    """Caso de uso para registrar un nuevo usuario dentro de una empresa."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(self, company_id_str: str, request: CreateUserRequest) -> UserResponse:
        """Registra un nuevo usuario aplicando las reglas de la arquitectura."""
        company_id = CompanyId.from_string(company_id_str)
        email_vo = Email(value=request.email)

        async with self.uow:
            # 1. Validar si ya existe el usuario por Email en la base de datos
            existing_user = await self.uow.users.find_by_email(email_vo)
            if existing_user:
                raise UserAlreadyExistsError(
                    f"Ya existe un usuario registrado con el correo '{request.email}'."
                )

            # 2. Envolver el hash de la contraseña
            password_hash = HashedPassword(value=f"hashed_{request.password}")

            # 3. Invocar la fábrica de dominio de la entidad rica
            user = User.register(
                email=email_vo,
                password_hash=password_hash,
                empresa_id=company_id,
                nombre=request.nombre,
                telefono=request.telefono,
            )

            # 4. Guardar a través del Unit of Work y confirmar la transacción
            await self.uow.users.save(user)
            await self.uow.commit()

            # 5. Retornar el DTO con el formato exacto del proyecto
            return UserResponse(
                id=str(user.id),
                email=user.email.value,
                nombre=user.nombre,
                empresa_id=str(user.empresa_id),
                telefono=user.telefono,
                activo=user.activo,
                created_at=user.created_at,
                updated_at=user.updated_at,
            )