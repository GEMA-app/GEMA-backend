import asyncio
import sys

from app.application.dtos import RegisterUserRequest
from app.application.use_cases.auth import RegisterUserUseCase
from app.domain.exceptions import CompanySlugExistsError, UserAlreadyExistsError
from app.infrastructure.events.bus import InProcessEventBus
from app.infrastructure.security.hashing import BcryptPasswordHasher
from app.infrastructure.security.jwt import PyJwtTokenService
from app.infrastructure.uow import SqlAlchemyUnitOfWork


async def seed_admin() -> None:
    """Siembra el usuario administrador base y la empresa por defecto en la base de datos."""
    print("Sembrando usuario base admin@gima.com...")
    event_bus = InProcessEventBus()
    uow = SqlAlchemyUnitOfWork(event_bus=event_bus)
    hasher = BcryptPasswordHasher()
    # PyJwtTokenService no necesita redis para generar tokens durante el registro
    token_service = PyJwtTokenService(None)  # type: ignore

    use_case = RegisterUserUseCase(uow, hasher, token_service)

    request = RegisterUserRequest(
        email="admin@gima.com",
        password="Password123!",
        nombre="Administrador General",
        company_name="GEMA S.A.",
        telefono="+582869600000",
    )

    try:
        await use_case.execute(request)
        print("¡Usuario admin@gima.com creado exitosamente junto con la empresa GEMA S.A.!")
    except UserAlreadyExistsError:
        print("El usuario admin@gima.com ya existe en el sistema.")
    except CompanySlugExistsError:
        print("La empresa GEMA S.A. (slug: gema-s-a) ya existe.")
    except Exception as e:
        print(f"Error inesperado al sembrar: {e}", file=sys.stderr)
        raise e


if __name__ == "__main__":
    asyncio.run(seed_admin())
