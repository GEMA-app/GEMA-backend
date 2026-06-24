import pytest
from datetime import datetime, UTC
from typing import Optional

from app.application.dtos.user_dtos import CreateUserRequest
from app.application.use_cases.user.create_user import CreateUserUseCase
from app.application.use_cases.user.get_user import GetUserUseCase
from app.domain.entities.user import User
from app.domain.exceptions.auth import UserAlreadyExistsError
from app.domain.exceptions.user import UserNotFoundError
from app.domain.value_objects import CompanyId, Email, UserId


# ==============================================================================
# SIMULACIONES (FAKES) PARA AISLAR LA LÓGICA DE NEGOCIO
# ==============================================================================

class FakeUserRepository:
    """Simula el comportamiento del repositorio de usuarios en memoria."""

    def __init__(self) -> None:
        self.users_db: dict[str, User] = {}

    async def save(self, user: User) -> None:
        self.users_db[str(user.id.value)] = user

    async def find_by_id(self, user_id: UserId) -> Optional[User]:
        return self.users_db.get(str(user_id.value))

    async def find_by_email(self, email: Email) -> Optional[User]:
        for user in self.users_db.values():
            if user.email.value == email.value:
                return user
        return None


class FakeUnitOfWork:
    """Simula el Unit of Work transaccional del proyecto."""

    def __init__(self) -> None:
        self.users = FakeUserRepository()
        self.committed = False

    async def __aenter__(self) -> "FakeUnitOfWork":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        pass

    async def commit(self) -> None:
        self.committed = True


# ==============================================================================
# PRUEBAS UNITARIAS DE LOS CASOS DE USO
# ==============================================================================

@pytest.mark.asyncio
async def test_create_user_use_case_success():
    """Verifica el registro exitoso de un usuario."""
    # Arrange
    uow = FakeUnitOfWork()
    use_case = CreateUserUseCase(uow=uow)
    
    request = CreateUserRequest(
        email="alejandro@gema.com",
        password="claveSegura123",
        nombre="Alejandro",
        telefono="+584120000000"
    )
    company_id = "11111111-1111-1111-1111-111111111111"

    # Act
    response = await use_case.execute(company_id_str=company_id, request=request)

    # Assert
    assert response.email == "alejandro@gema.com"
    assert response.nombre == "Alejandro"
    assert response.activo is True
    assert uow.committed is True


@pytest.mark.asyncio
async def test_create_user_use_case_duplicate_email():
    """Verifica que no se permitan emails duplicados."""
    # Arrange
    uow = FakeUnitOfWork()
    use_case = CreateUserUseCase(uow=uow)
    company_id = "11111111-1111-1111-1111-111111111111"

    # Registrar un usuario previo con el mismo email en el fake
    existing_user = User(
        id=UserId.from_string("22222222-2222-2222-2222-222222222222"),
        email=Email(value="duplicado@gema.com"),
        password_hash=None,
        empresa_id=CompanyId.from_string(company_id),
        nombre="Usuario Viejo"
    )
    await uow.users.save(existing_user)

    request = CreateUserRequest(
        email="duplicado@gema.com",
        password="otraClave",
        nombre="Usuario Nuevo"
    )

    # Act & Assert
    with pytest.raises(UserAlreadyExistsError):
        await use_case.execute(company_id_str=company_id, request=request)


@pytest.mark.asyncio
async def test_get_user_use_case_not_found():
    """Verifica el lanzamiento de UserNotFoundError si el ID no existe."""
    # Arrange
    uow = FakeUnitOfWork()
    use_case = GetUserUseCase(uow=uow)
    random_id = "99999999-9999-9999-9999-999999999999"

    # Act & Assert
    with pytest.raises(UserNotFoundError):
        await use_case.execute(user_id_str=random_id)