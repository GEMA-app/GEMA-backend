"""Caso de uso para listar usuarios de una empresa."""
from dataclasses import dataclass
from datetime import UTC, datetime

from app.application.dtos.user_dtos import UserResponse
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.value_objects import CompanyId


@dataclass
class ListUsersUseCase:
    """Lista todos los usuarios pertenecientes a una empresa (tenant)."""

    uow: UnitOfWorkPort

    async def execute(self, empresa_id_str: str) -> list[UserResponse]:
        """Ejecuta la consulta de todos los usuarios de la empresa.

        Args:
            empresa_id_str: Identificador UUID en string de la empresa.

        Returns:
            Lista de respuestas con los datos de cada usuario.
        """
        company_id = CompanyId.from_string(empresa_id_str)
        async with self.uow:
            users = await self.uow.users.list_by_company(company_id)
            return [UserResponse(
                id=str(u.id.value),
                email=u.email.value,
                nombre=u.nombre,
                telefono=u.telefono,
                activo=u.activo,
                empresa_id=str(u.empresa_id.value),
                created_at=u.created_at or datetime.now(UTC),
                updated_at=u.updated_at or datetime.now(UTC),
                roles=[r.nombre for r in u.roles],
            ) for u in users]
