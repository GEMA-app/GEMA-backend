from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.preference_repository import PreferenceRepositoryPort
from app.domain.entities import UserPreference
from app.domain.enums import Theme
from app.domain.events import DomainEvent
from app.domain.value_objects import CompanyId, UserId
from app.infrastructure.db.models.preferences import UserPreferenceModel
from app.infrastructure.repositories.base import SqlAlchemyRepository


class SqlAlchemyPreferenceRepository(
    SqlAlchemyRepository[UserPreferenceModel, UserPreference, UserId],
    PreferenceRepositoryPort,
):
    """Implementación en SQLAlchemy para el puerto de Preferencias."""

    pk_column = "usuario_id"

    def __init__(
        self, session: AsyncSession, pending_events: list[DomainEvent] | None = None
    ) -> None:
        super().__init__(session, UserPreferenceModel, pending_events)

    def _to_model(self, entity: UserPreference) -> UserPreferenceModel:
        return UserPreferenceModel(
            usuario_id=entity.usuario_id.value,
            empresa_id=entity.empresa_id.value,
            tema=entity.tema.value,
        )

    def _to_entity(self, model: UserPreferenceModel) -> UserPreference:
        return UserPreference(
            usuario_id=UserId(model.usuario_id),
            empresa_id=CompanyId(model.empresa_id),
            tema=Theme(model.tema),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def get_by_user(
        self, usuario_id: UserId, empresa_id: CompanyId
    ) -> UserPreference | None:
        """Obtiene las preferencias de un usuario en una empresa."""
        stmt = select(UserPreferenceModel).where(
            UserPreferenceModel.usuario_id == usuario_id.value,
            UserPreferenceModel.empresa_id == empresa_id.value,
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_entity(model)
