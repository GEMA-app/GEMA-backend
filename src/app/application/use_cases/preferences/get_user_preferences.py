from app.application.dtos.preference_dtos import PreferenceResponse
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.exceptions import PreferenceNotFoundError
from app.domain.value_objects import CompanyId, UserId


class GetUserPreferencesUseCase:
    """Obtiene las preferencias del usuario autenticado."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(
        self, company_id_str: str, user_id_str: str
    ) -> PreferenceResponse:
        company_id = CompanyId.from_string(company_id_str)
        user_id = UserId.from_string(user_id_str)

        async with self.uow:  # Solo abre sesión de lectura; no necesita commit
            pref = await self.uow.preferences.get_by_user(user_id, company_id)
            if not pref:
                raise PreferenceNotFoundError(
                    f"No se encontraron preferencias para el usuario "
                    f"'{user_id_str}' en la empresa '{company_id_str}'."
                )

            return PreferenceResponse(
                usuario_id=str(pref.usuario_id),
                empresa_id=str(pref.empresa_id),
                tema=pref.tema.value,
            )