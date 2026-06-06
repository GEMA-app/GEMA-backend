from app.application.dtos.preferences_dtos import (
    PreferenceResponse,
    UpdatePreferenceRequest,
)
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.entities import UserPreference
from app.domain.enums import Theme
from app.domain.exceptions import PreferenceThemeInvalidError
from app.domain.value_objects import CompanyId, UserId


class UpdateUserPreferencesUseCase:
    """
    Actualiza las preferencias del usuario autenticado.
    Si no existen, crea un registro con valores por defecto (upsert).
    """

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(
        self,
        company_id_str: str,
        user_id_str: str,
        request: UpdatePreferenceRequest,
    ) -> PreferenceResponse:
        company_id = CompanyId.from_string(company_id_str)
        user_id = UserId.from_string(user_id_str)

        async with self.uow:
            pref = await self.uow.preferences.get_by_user(user_id, company_id)

            if not pref:
                pref = UserPreference.create(
                    usuario_id=user_id,
                    empresa_id=company_id,
                )

            if request.tema is not None:
                try:
                    pref.tema = Theme(request.tema)
                except ValueError:
                    temas_validos = ", ".join(t.value for t in Theme)
                    raise PreferenceThemeInvalidError(
                        f"El tema '{request.tema}' no es válido. "
                        f"Valores permitidos: {temas_validos}."
                    )

            await self.uow.preferences.save(pref)
            await self.uow.commit()

            return PreferenceResponse(
                usuario_id=str(pref.usuario_id),
                empresa_id=str(pref.empresa_id),
                tema=pref.tema.value,
            )