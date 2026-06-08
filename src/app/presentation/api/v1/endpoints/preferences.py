
from fastapi import APIRouter, Depends

from app.application.dtos.auth_dtos import UserResponse
from app.application.dtos.preferences_dtos import (
    UpdatePreferenceRequest as UpdatePreferenceDTO,
)
from app.application.use_cases.preferences import (
    GetUserPreferencesUseCase,
    UpdateUserPreferencesUseCase,
)
from app.composition.container import (
    get_update_preferences_use_case,
    provide_user_preferences_use_case,
)
from app.domain.enums import PermissionModule
from app.presentation.api.v1.endpoints.dependencies import (
    require_permission,
)
from app.presentation.api.v1.schemas.preferences import (
    PreferenceAttributes,
    PreferenceDocument,
    PreferenceResource,
    UpdatePreferenceRequest,
)

router = APIRouter()


# GET /companies/{company_id}/me/preferences
@router.get(
    "",
    response_model=PreferenceDocument,
    summary="Obtener preferencias del usuario actual",
)
async def get_preferences(
    company_id: str,
    current_user: UserResponse = Depends(require_permission(PermissionModule.PREFERENCES, "view")),
    use_case: GetUserPreferencesUseCase = Depends(provide_user_preferences_use_case),
) -> PreferenceDocument:
    """Obtiene las preferencias del usuario autenticado."""
    res = await use_case.execute(company_id, current_user.id)
    return PreferenceDocument(
        data=PreferenceResource(
            id=res.usuario_id,
            attributes=PreferenceAttributes(
                empresa_id=res.empresa_id,
                tema=res.tema,
            ),
        )
    )


# PATCH /companies/{company_id}/me/preferences
@router.patch(
    "",
    response_model=PreferenceDocument,
    summary="Actualizar preferencias del usuario actual",
)
async def update_preferences(
    company_id: str,
    request: UpdatePreferenceRequest,
    current_user: UserResponse = Depends(require_permission(PermissionModule.PREFERENCES, "edit")),
    use_case: UpdateUserPreferencesUseCase = Depends(get_update_preferences_use_case),
) -> PreferenceDocument:
    """Actualiza las preferencias del usuario autenticado."""
    # request.data.id se ignora intencionalmente.
    # El servidor identifica al usuario por el token JWT, no por el body.
    # JSON:API exige el campo id en PATCH, pero no lo usamos para evitar
    # que un cliente malintencionado intente actualizar otro perfil.
    dto = UpdatePreferenceDTO(
        tema=request.data.attributes.tema,
    )
    res = await use_case.execute(company_id, current_user.id, dto)
    return PreferenceDocument(
        data=PreferenceResource(
            id=res.usuario_id,
            attributes=PreferenceAttributes(
                empresa_id=res.empresa_id,
                tema=res.tema,
            ),
        )
    )
