"""Unidad de Trabajo (Unit of Work) con SQLAlchemy asíncrono."""

from typing import Any, Self

import structlog
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.application.ports.event_bus import EventBusPort
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.events import DomainEvent
from app.domain.exceptions import EventPublishError
from app.infrastructure.db.session import async_session_factory
from app.infrastructure.repositories.article_category_repository import (
    SqlAlchemyArticleCategoryRepository,
)
from app.infrastructure.repositories.asset_repository import SqlAlchemyAssetRepository
from app.infrastructure.repositories.asset_state_log_repository import (
    SqlAlchemyAssetStateLogRepository,
)
from app.infrastructure.repositories.catalog_article_repository import (
    SqlAlchemyCatalogArticleRepository,
)
from app.infrastructure.repositories.company_repository import SqlAlchemyCompanyRepository
from app.infrastructure.repositories.failure_report_repository import (
    SqlAlchemyFailureReportRepository,
)
from app.infrastructure.repositories.intervention_repository import SqlAlchemyInterventionRepository
from app.infrastructure.repositories.inventory_part_repository import (
    SqlAlchemyInventoryPartRepository,
)
from app.infrastructure.repositories.location_repository import SqlAlchemyLocationRepository
from app.infrastructure.repositories.maintenance_plan_repository import (
    SqlAlchemyMaintenancePlanRepository,
)
from app.infrastructure.repositories.plan_execution_repository import (
    SqlAlchemyPlanExecutionRepository,
)
from app.infrastructure.repositories.preference_repository import SqlAlchemyPreferenceRepository
from app.infrastructure.repositories.role_repository import SqlAlchemyRoleRepository
from app.infrastructure.repositories.subscription_plan_repository import (
    SqlAlchemySubscriptionPlanRepository,
)
from app.infrastructure.repositories.system_audit_repository import SqlAlchemySystemAuditRepository
from app.infrastructure.repositories.used_part_repository import SqlAlchemyUsedPartRepository
from app.infrastructure.repositories.user_repository import SqlAlchemyUserRepository
from app.infrastructure.repositories.work_order_repository import SqlAlchemyWorkOrderRepository

logger = structlog.get_logger()


class SqlAlchemyUnitOfWork(UnitOfWorkPort):
    """Implementación de UnitOfWorkPort utilizando SQLAlchemy 2.0 y AsyncSession."""

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession] = async_session_factory,
        event_bus: EventBusPort | None = None,
    ) -> None:
        """Inicializa el Unit of Work con una fábrica de sesiones y un bus de eventos opcional."""
        self.session_factory = session_factory
        if event_bus is None:
            from app.infrastructure.events.bus import InProcessEventBus

            self.event_bus: EventBusPort = InProcessEventBus()
        else:
            self.event_bus = event_bus
        self._pending_events: list[DomainEvent] = []

    async def __aenter__(self) -> Self:
        """Inicia la sesión asíncrona y construye los repositorios asociados a ella."""
        self.session = self.session_factory()
        self._pending_events.clear()
        self.users = SqlAlchemyUserRepository(self.session, self._pending_events)
        self.companies = SqlAlchemyCompanyRepository(self.session, self._pending_events)
        self.roles = SqlAlchemyRoleRepository(self.session, self._pending_events)
        self.assets = SqlAlchemyAssetRepository(self.session, self._pending_events)
        self.failure_reports = SqlAlchemyFailureReportRepository(self.session, self._pending_events)
        self.asset_state_logs = SqlAlchemyAssetStateLogRepository(
            self.session, self._pending_events
        )
        self.catalog_articles = SqlAlchemyCatalogArticleRepository(
            self.session, self._pending_events
        )
        self.locations = SqlAlchemyLocationRepository(self.session, self._pending_events)
        self.preferences = SqlAlchemyPreferenceRepository(self.session, self._pending_events)
        self.article_categories = SqlAlchemyArticleCategoryRepository(
            self.session, self._pending_events
        )
        self.subscription_plans = SqlAlchemySubscriptionPlanRepository(
            self.session, self._pending_events
        )
        self.system_audits = SqlAlchemySystemAuditRepository(self.session, self._pending_events)
        self.maintenance_plans = SqlAlchemyMaintenancePlanRepository(
            self.session, self._pending_events
        )
        self.used_parts = SqlAlchemyUsedPartRepository(self.session, self._pending_events)
        self.inventory_parts = SqlAlchemyInventoryPartRepository(self.session)
        self.work_orders = SqlAlchemyWorkOrderRepository(self.session, self._pending_events)
        self.plan_executions = SqlAlchemyPlanExecutionRepository(self.session, self._pending_events)
        self.interventions = SqlAlchemyInterventionRepository(self.session, self._pending_events)
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, tb: Any) -> None:
        """Cierra la sesión de base de datos.

        Ejecuta rollback si ocurrió una excepción o limpia transacciones exitosas.

        Args:
            exc_type: Tipo de excepción que ocurrió dentro del contexto, o None.
            exc_val: Valor de la excepción que ocurrió, o None.
            tb: Traceback de la excepción que ocurrió, o None.
        """
        try:
            if exc_type is not None:
                try:
                    await self.rollback()
                except Exception as e:
                    logger.error("Rollback falló en __aexit__", error=str(e))
        finally:
            self._pending_events.clear()
            if hasattr(self, "session"):
                await self.session.close()

    async def commit(self) -> None:
        """Confirma la transacción actual en la base de datos.

        Despacha eventos de dominio despachados con éxito.
        """
        await self.session.commit()

        if self._pending_events:
            events_to_publish = list(self._pending_events)
            self._pending_events.clear()
            try:
                await self.event_bus.publish(events_to_publish)
            except Exception as e:
                logger.error(
                    "Fallo al publicar eventos de dominio después del commit",
                    error=str(e),
                    event_count=len(events_to_publish),
                )
                raise EventPublishError(
                    f"Error al publicar {len(events_to_publish)} eventos de dominio: {e}"
                ) from e

    async def rollback(self) -> None:
        """Deshace los cambios pendientes en la transacción actual y limpia eventos."""
        await self.session.rollback()
        self._pending_events.clear()
