from dataclasses import dataclass
from datetime import datetime

from app.domain.enums import Theme
from app.domain.exceptions import PreferenceThemeInvalidError
from app.domain.value_objects import CompanyId, UserId


@dataclass
class UserPreference:
    """Preferencias de interfaz de usuario para un usuario en una empresa."""

    usuario_id: UserId
    empresa_id: CompanyId
    tema: Theme
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @classmethod
    def create(
        cls,
        usuario_id: UserId,
        empresa_id: CompanyId,
        tema: Theme = Theme.DARK,
    ) -> "UserPreference":
        """Crea preferencias con valores por defecto y valida invariantes."""
        return cls(
            usuario_id=usuario_id,
            empresa_id=empresa_id,
            tema=tema,
        )

    def __post_init__(self) -> None:
        """Valida invariantes después de la inicialización."""
        if self.tema is None:
            raise PreferenceThemeInvalidError(
                "El tema visual no puede estar vacío."
            )

    def change_theme(self, nuevo_tema: str) -> None:
        """Cambia el tema visual. Acepta str para que la validación sea en dominio."""
        try:
            tema_validado = Theme(nuevo_tema)
        except ValueError:
            raise PreferenceThemeInvalidError(
                f"El tema '{nuevo_tema}' no es válido. "
                f"Valores permitidos: {', '.join(t.value for t in Theme)}."
            ) from None
        self.tema = tema_validado
