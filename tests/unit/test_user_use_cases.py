"""Pruebas unitarias CRUD para los casos de uso del módulo User.

Cubre: CreateUserUseCase, GetUserUseCase, EditUserUseCase,
       DeleteUserUseCase y ListUsersUseCase con todos sus caminos
       (éxito, no encontrado, duplicado, baja lógica).
"""

from unittest.mock import MagicMock

import pytest

from app.application.dtos.user_dtos import CreateUserRequest, UpdateUserRequest
from app.application.use_cases.user.create_user import CreateUserUseCase
from app.application.use_cases.user.delete_user import DeleteUserUseCase
from app.application.use_cases.user.edit_user import EditUserUseCase
from app.application.use_cases.user.get_user import GetUserUseCase
from app.application.use_cases.user.list_users import ListUsersUseCase
from app.domain.entities.user import User
from app.domain.exceptions import UserAlreadyExistsError
from app.domain.exceptions.user import UserNotFoundError
from app.domain.value_objects import CompanyId, Email, HashedPassword, UserId

# ==============================================================================
# CONSTANTES DE PRUEBA
# ==============================================================================

COMPANY_ID = "11111111-1111-1111-1111-111111111111"
USER_ID = "22222222-2222-2222-2222-222222222222"
OTHER_USER_ID = "33333333-3333-3333-3333-333333333333"
TEST_EMAIL = "alejandro@gema.com"
TEST_PASSWORD = "ClaveSegura123!"
TEST_NOMBRE = "Alejandro Rodríguez"

# ==============================================================================
# INFRAESTRUCTURA FALSA (FAKES) PARA AISLAR LA LÓGICA DE NEGOCIO
# ==============================================================================


class FakeUserRepository:
    """Simula el comportamiento del repositorio de usuarios en memoria."""

    def __init__(self) -> None:
        self.users_db: dict[str, User] = {}

    async def save(self, user: User) -> None:
        """Guarda o actualiza un usuario en el almacén en memoria."""
        self.users_db[str(user.id.value)] = user

    async def get_by_id(self, user_id: UserId) -> User | None:
        """Busca un usuario por su ID único."""
        return self.users_db.get(str(user_id.value))

    async def get_by_email(self, email: Email) -> User | None:
        """Busca un usuario por su dirección de correo electrónico."""
        for user in self.users_db.values():
            if user.email.value == email.value:
                return user
        return None

    async def list_by_company(self, empresa_id: CompanyId) -> list[User]:
        """Lista todos los usuarios de una empresa específica."""
        return [u for u in self.users_db.values() if u.empresa_id.value == empresa_id.value]

    async def delete(self, user_id: UserId) -> None:
        """Elimina físicamente un usuario (solo para tests de infraestructura)."""
        self.users_db.pop(str(user_id.value), None)


class FakeHasher:
    """Simula el servicio de hashing de contraseñas sin criptografía real."""

    def hash(self, password: str) -> str:
        """Retorna un hash simulado determinístico."""
        return f"hashed_{password}"

    def verify(self, plain: str, hashed: str) -> bool:
        """Verifica un hash simulado."""
        return hashed == f"hashed_{plain}"


class FakeUnitOfWork:
    """Simula el Unit of Work transaccional del proyecto."""

    def __init__(self) -> None:
        self.users = FakeUserRepository()
        self.committed = False

    async def __aenter__(self) -> "FakeUnitOfWork":
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: type[BaseException] | None,
    ) -> None:
        pass

    async def commit(self) -> None:
        """Simula el commit de la transacción."""
        self.committed = True

    async def rollback(self) -> None:
        """Simula el rollback de la transacción."""
        pass


def _make_user(
    user_id: str = USER_ID,
    email: str = TEST_EMAIL,
    company_id: str = COMPANY_ID,
    nombre: str = TEST_NOMBRE,
    activo: bool = True,
) -> User:
    """Fábrica de dominio para crear usuarios de prueba de forma concisa."""
    return User(
        id=UserId.from_string(user_id),
        email=Email(value=email),
        password_hash=HashedPassword(value="hashed_clave"),
        empresa_id=CompanyId.from_string(company_id),
        nombre=nombre,
        activo=activo,
    )


# ==============================================================================
# TESTS: CreateUserUseCase
# ==============================================================================


class TestCreateUserUseCase:
    """Casos de uso: registro de un nuevo usuario."""

    @pytest.mark.asyncio
    async def test_crea_usuario_exitosamente(self) -> None:
        """Verifica que un usuario nuevo se persiste y el commit ocurre."""
        # Arrange
        uow = FakeUnitOfWork()
        use_case = CreateUserUseCase(uow=uow, hasher=FakeHasher())
        request = CreateUserRequest(
            email=TEST_EMAIL,
            password=TEST_PASSWORD,
            nombre=TEST_NOMBRE,
            telefono="+584120000000",
        )

        # Act
        response = await use_case.execute(company_id_str=COMPANY_ID, request=request)

        # Assert
        assert response.email == TEST_EMAIL
        assert response.nombre == TEST_NOMBRE
        assert response.activo is True
        assert response.empresa_id == COMPANY_ID
        assert response.telefono == "+584120000000"
        assert uow.committed is True

    @pytest.mark.asyncio
    async def test_crea_usuario_sin_telefono(self) -> None:
        """Verifica que el teléfono es opcional y puede ser None."""
        uow = FakeUnitOfWork()
        use_case = CreateUserUseCase(uow=uow, hasher=FakeHasher())
        request = CreateUserRequest(
            email="sin.telefono@gema.com",
            password=TEST_PASSWORD,
            nombre="Usuario Sin Teléfono",
        )

        response = await use_case.execute(company_id_str=COMPANY_ID, request=request)

        assert response.telefono is None
        assert uow.committed is True

    @pytest.mark.asyncio
    async def test_falla_con_email_duplicado(self) -> None:
        """Verifica que no se permiten dos usuarios con el mismo email."""
        # Arrange: usuario previo con el mismo email
        uow = FakeUnitOfWork()
        await uow.users.save(_make_user(email=TEST_EMAIL))

        use_case = CreateUserUseCase(uow=uow, hasher=FakeHasher())
        request = CreateUserRequest(
            email=TEST_EMAIL,
            password="otraClave123!",
            nombre="Otro Usuario",
        )

        # Act & Assert
        with pytest.raises(UserAlreadyExistsError):
            await use_case.execute(company_id_str=COMPANY_ID, request=request)

    @pytest.mark.asyncio
    async def test_persiste_usuario_en_repositorio(self) -> None:
        """Verifica que el usuario queda guardado en el repositorio tras ejecutar el use case."""
        uow = FakeUnitOfWork()
        use_case = CreateUserUseCase(uow=uow, hasher=FakeHasher())
        request = CreateUserRequest(
            email="persistido@gema.com",
            password=TEST_PASSWORD,
            nombre="Persistido",
        )

        response = await use_case.execute(company_id_str=COMPANY_ID, request=request)

        # El usuario debe existir en el repositorio por ID
        saved_user = await uow.users.get_by_id(UserId.from_string(response.id))
        assert saved_user is not None
        assert saved_user.email.value == "persistido@gema.com"

    @pytest.mark.asyncio
    async def test_hasher_es_llamado_con_la_clave_correcta(self) -> None:
        """Verifica que el PasswordHasher recibe la contraseña en texto plano."""
        hasher_mock = MagicMock()
        hasher_mock.hash.return_value = "hashed_resultado"

        uow = FakeUnitOfWork()
        use_case = CreateUserUseCase(uow=uow, hasher=hasher_mock)
        request = CreateUserRequest(
            email="hash.test@gema.com",
            password="MiClave123!",
            nombre="Test Hash",
        )

        await use_case.execute(company_id_str=COMPANY_ID, request=request)

        hasher_mock.hash.assert_called_once_with("MiClave123!")


# ==============================================================================
# TESTS: GetUserUseCase
# ==============================================================================


class TestGetUserUseCase:
    """Casos de uso: consulta de un usuario por ID."""

    @pytest.mark.asyncio
    async def test_obtiene_usuario_existente(self) -> None:
        """Verifica que se retornan los datos correctos de un usuario existente."""
        # Arrange
        uow = FakeUnitOfWork()
        await uow.users.save(_make_user())
        use_case = GetUserUseCase(uow=uow)

        # Act
        response = await use_case.execute(user_id_str=USER_ID)

        # Assert
        assert response.id == USER_ID
        assert response.email == TEST_EMAIL
        assert response.nombre == TEST_NOMBRE
        assert response.empresa_id == COMPANY_ID
        assert response.activo is True

    @pytest.mark.asyncio
    async def test_lanza_user_not_found_si_id_inexistente(self) -> None:
        """Verifica que UserNotFoundError se lanza si no existe el ID."""
        uow = FakeUnitOfWork()
        use_case = GetUserUseCase(uow=uow)

        with pytest.raises(UserNotFoundError):
            await use_case.execute(user_id_str="99999999-9999-9999-9999-999999999999")

    @pytest.mark.asyncio
    async def test_retorna_usuario_inactivo_sin_error(self) -> None:
        """Un usuario inactivo puede ser consultado (solo el login falla)."""
        uow = FakeUnitOfWork()
        await uow.users.save(_make_user(activo=False))
        use_case = GetUserUseCase(uow=uow)

        response = await use_case.execute(user_id_str=USER_ID)

        assert response.activo is False


# ==============================================================================
# TESTS: EditUserUseCase
# ==============================================================================


class TestEditUserUseCase:
    """Casos de uso: actualización parcial de un usuario."""

    @pytest.mark.asyncio
    async def test_actualiza_nombre_exitosamente(self) -> None:
        """Verifica que el nombre se actualiza y el commit ocurre."""
        # Arrange
        uow = FakeUnitOfWork()
        await uow.users.save(_make_user())
        use_case = EditUserUseCase(uow=uow)

        request = UpdateUserRequest(nombre="Nuevo Nombre")

        # Act
        response = await use_case.execute(user_id_str=USER_ID, request=request)

        # Assert
        assert response.nombre == "Nuevo Nombre"
        assert uow.committed is True

    @pytest.mark.asyncio
    async def test_actualiza_email_exitosamente(self) -> None:
        """Verifica que el email se actualiza correctamente."""
        uow = FakeUnitOfWork()
        await uow.users.save(_make_user())
        use_case = EditUserUseCase(uow=uow)

        response = await use_case.execute(
            user_id_str=USER_ID,
            request=UpdateUserRequest(email="nuevo@gema.com"),
        )

        assert response.email == "nuevo@gema.com"

    @pytest.mark.asyncio
    async def test_actualiza_telefono_exitosamente(self) -> None:
        """Verifica que el teléfono se actualiza correctamente."""
        uow = FakeUnitOfWork()
        await uow.users.save(_make_user())
        use_case = EditUserUseCase(uow=uow)

        response = await use_case.execute(
            user_id_str=USER_ID,
            request=UpdateUserRequest(telefono="+584140001111"),
        )

        assert response.telefono == "+584140001111"

    @pytest.mark.asyncio
    async def test_desactiva_usuario_via_activo_false(self) -> None:
        """Verifica que activo=False llama a user.deactivate() correctamente."""
        uow = FakeUnitOfWork()
        await uow.users.save(_make_user(activo=True))
        use_case = EditUserUseCase(uow=uow)

        response = await use_case.execute(
            user_id_str=USER_ID,
            request=UpdateUserRequest(activo=False),
        )

        assert response.activo is False

    @pytest.mark.asyncio
    async def test_reactiva_usuario_via_activo_true(self) -> None:
        """Verifica que activo=True llama a user.activate() correctamente."""
        uow = FakeUnitOfWork()
        await uow.users.save(_make_user(activo=False))
        use_case = EditUserUseCase(uow=uow)

        response = await use_case.execute(
            user_id_str=USER_ID,
            request=UpdateUserRequest(activo=True),
        )

        assert response.activo is True

    @pytest.mark.asyncio
    async def test_campos_none_no_se_modifican(self) -> None:
        """Verifica que pasar None en campos opcionales no altera los valores existentes."""
        uow = FakeUnitOfWork()
        await uow.users.save(_make_user(nombre=TEST_NOMBRE))
        use_case = EditUserUseCase(uow=uow)

        # Request completamente vacío (todos None)
        response = await use_case.execute(
            user_id_str=USER_ID,
            request=UpdateUserRequest(),
        )

        # El nombre no debe haber cambiado
        assert response.nombre == TEST_NOMBRE

    @pytest.mark.asyncio
    async def test_lanza_user_not_found_si_id_inexistente(self) -> None:
        """Verifica que UserNotFoundError se lanza si el usuario no existe."""
        uow = FakeUnitOfWork()
        use_case = EditUserUseCase(uow=uow)

        with pytest.raises(UserNotFoundError):
            await use_case.execute(
                user_id_str="99999999-9999-9999-9999-999999999999",
                request=UpdateUserRequest(nombre="Nadie"),
            )


# ==============================================================================
# TESTS: DeleteUserUseCase (Baja Lógica)
# ==============================================================================


class TestDeleteUserUseCase:
    """Casos de uso: baja lógica de un usuario (activo → False)."""

    @pytest.mark.asyncio
    async def test_desactiva_usuario_exitosamente(self) -> None:
        """Verifica que el usuario queda inactivo tras la baja lógica."""
        # Arrange
        uow = FakeUnitOfWork()
        await uow.users.save(_make_user(activo=True))
        use_case = DeleteUserUseCase(uow=uow)

        # Act
        response = await use_case.execute(user_id_str=USER_ID)

        # Assert
        assert response.activo is False
        assert uow.committed is True

    @pytest.mark.asyncio
    async def test_baja_logica_no_elimina_fisicamente(self) -> None:
        """Verifica que el registro aún existe en el repositorio tras la baja."""
        uow = FakeUnitOfWork()
        await uow.users.save(_make_user())
        use_case = DeleteUserUseCase(uow=uow)

        await use_case.execute(user_id_str=USER_ID)

        # El usuario sigue en la base de datos (solo marcado como inactivo)
        persisted = await uow.users.get_by_id(UserId.from_string(USER_ID))
        assert persisted is not None
        assert persisted.activo is False

    @pytest.mark.asyncio
    async def test_lanza_user_not_found_si_id_inexistente(self) -> None:
        """Verifica que UserNotFoundError se lanza si el usuario no existe."""
        uow = FakeUnitOfWork()
        use_case = DeleteUserUseCase(uow=uow)

        with pytest.raises(UserNotFoundError):
            await use_case.execute(user_id_str="99999999-9999-9999-9999-999999999999")

    @pytest.mark.asyncio
    async def test_retorna_datos_completos_del_usuario_desactivado(self) -> None:
        """Verifica que la respuesta incluye todos los campos del usuario desactivado."""
        uow = FakeUnitOfWork()
        await uow.users.save(_make_user(nombre=TEST_NOMBRE))
        use_case = DeleteUserUseCase(uow=uow)

        response = await use_case.execute(user_id_str=USER_ID)

        assert response.id == USER_ID
        assert response.email == TEST_EMAIL
        assert response.nombre == TEST_NOMBRE
        assert response.empresa_id == COMPANY_ID


# ==============================================================================
# TESTS: ListUsersUseCase
# ==============================================================================


class TestListUsersUseCase:
    """Casos de uso: listado de usuarios por empresa."""

    @pytest.mark.asyncio
    async def test_retorna_lista_vacia_cuando_no_hay_usuarios(self) -> None:
        """Verifica que una empresa sin usuarios retorna lista vacía."""
        uow = FakeUnitOfWork()
        use_case = ListUsersUseCase(uow=uow)

        result = await use_case.execute(empresa_id_str=COMPANY_ID)

        assert result == []

    @pytest.mark.asyncio
    async def test_retorna_usuarios_de_la_empresa(self) -> None:
        """Verifica que se listan correctamente los usuarios de la empresa."""
        uow = FakeUnitOfWork()
        await uow.users.save(_make_user(user_id=USER_ID, email="user1@gema.com"))
        await uow.users.save(
            _make_user(user_id=OTHER_USER_ID, email="user2@gema.com")
        )
        use_case = ListUsersUseCase(uow=uow)

        result = await use_case.execute(empresa_id_str=COMPANY_ID)

        assert len(result) == 2
        emails = {r.email for r in result}
        assert "user1@gema.com" in emails
        assert "user2@gema.com" in emails

    @pytest.mark.asyncio
    async def test_no_retorna_usuarios_de_otra_empresa(self) -> None:
        """Verifica el aislamiento de tenant: no se mezclan usuarios de diferentes empresas."""
        uow = FakeUnitOfWork()
        other_company = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"

        # Usuario de la empresa destino
        await uow.users.save(_make_user(user_id=USER_ID, email="mio@gema.com"))
        # Usuario de otra empresa
        await uow.users.save(
            _make_user(user_id=OTHER_USER_ID, email="ajeno@gema.com", company_id=other_company)
        )
        use_case = ListUsersUseCase(uow=uow)

        result = await use_case.execute(empresa_id_str=COMPANY_ID)

        assert len(result) == 1
        assert result[0].email == "mio@gema.com"

    @pytest.mark.asyncio
    async def test_respuesta_contiene_campos_completos(self) -> None:
        """Verifica que cada UserResponse contiene todos los campos esperados."""
        uow = FakeUnitOfWork()
        await uow.users.save(_make_user())
        use_case = ListUsersUseCase(uow=uow)

        result = await use_case.execute(empresa_id_str=COMPANY_ID)

        assert len(result) == 1
        r = result[0]
        assert r.id == USER_ID
        assert r.email == TEST_EMAIL
        assert r.empresa_id == COMPANY_ID
        assert r.activo is True
        assert r.created_at is not None
        assert r.updated_at is not None
