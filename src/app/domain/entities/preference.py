"""Entidad UserPreference — preferencias de interfaz de usuario por empresa."""

from dataclasses import dataclass, field
from datetime import datetime

from app.domain.enums import Theme
from app.domain.events import DomainEvent, EventProducer
from app.domain.exceptions import PreferenceThemeInvalidError
from app.domain.value_objects import CompanyId, UserId


@dataclass
class UserPreference(EventProducer):
    """Preferencias de interfaz de usuario para un usuario en una empresa."""

    usuario_id: UserId
    empresa_id: CompanyId
    tema: Theme
    created_at: datetime | None = None
    updated_at: datetime | None = None
    version: int = 1
    _events: list[DomainEvent] = field(default_factory=list, init=False, repr=False)

    @classmethod
    def create(
        cls,
        usuario_id: UserId,
        empresa_id: CompanyId,
        tema: Theme = Theme.DARK,
    ) -> "UserPreference":
        """Crea preferencias con valores por defecto y valida invariantes.

        Args:
            usuario_id: Identificador del usuario propietario.
            empresa_id: Identificador de la empresa a la que pertenece.
            tema: Tema visual inicial (por defecto DARK).

        Returns:
            Las nuevas preferencias de usuario creadas.
        """
        return cls(
            usuario_id=usuario_id,
            empresa_id=empresa_id,
            tema=tema,
        )

    def __post_init__(self) -> None:
        """Valida invariantes después de la inicialización.

        Raises:
            PreferenceThemeInvalidError: Si el tema visual está vacío.
        """
        if self.tema is None:
            raise PreferenceThemeInvalidError(
                "El tema visual no puede estar vacío."
            )

    def pull_events(self) -> list[DomainEvent]:
        """Devuelve los eventos de dominio acumulados y limpia la lista interna.

        Returns:
            La lista de eventos de dominio acumulados, vaciando la lista interna.
        """
        events = self._events.copy()
        self._events.clear()
        return events

    def change_theme(self, nuevo_tema: str) -> None:
        """Cambia el tema visual. Acepta str para que la validación sea en dominio.

        Args:
            nuevo_tema: El nuevo tema visual a aplicar.

        Raises:
            PreferenceThemeInvalidError: Si el tema no es uno de los valores válidos.
        """
        try:
            tema_validado = Theme(nuevo_tema)
        except ValueError:
            raise PreferenceThemeInvalidError(
                f"El tema '{nuevo_tema}' no es válido. "
                f"Valores permitidos: {', '.join(t.value for t in Theme)}."
            ) from None
        self.tema = tema_validado
