"""Repositorio de reportes de falla con SQLAlchemy asíncrono."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.failure_report_repository import FailureReportRepositoryPort
from app.domain.entities import FailureReport
from app.domain.enums import PriorityLevel, ReportStatus
from app.domain.events import DomainEvent
from app.domain.value_objects import CompanyId, FailureReportId
from app.infrastructure.db.models.failure_report import FailureReportModel
from app.infrastructure.repositories.tenant_repository import SqlAlchemyTenantRepository


class SqlAlchemyFailureReportRepository(
    SqlAlchemyTenantRepository[FailureReportModel, FailureReport, FailureReportId],
    FailureReportRepositoryPort,
):
    """Implementación en SQLAlchemy para el puerto de repositorio de Reportes de Falla."""

    pk_column: str = "id"

    def __init__(
        self, session: AsyncSession, pending_events: list[DomainEvent] | None = None
    ) -> None:
        super().__init__(session, FailureReportModel, pending_events)

    def _to_model(self, entity: FailureReport) -> FailureReportModel:
        return FailureReportModel(
            id=entity.id.value,
            empresa_id=entity.empresa_id.value,
            title=entity.title,
            description=entity.description,
            location=entity.location,
            priority=entity.priority.value,
            reported_by=entity.reported_by,
            status=entity.status.value,
            version=entity.version,
        )

    def _to_entity(self, model: FailureReportModel) -> FailureReport:
        return FailureReport(
            id=FailureReportId(model.id),
            empresa_id=CompanyId(model.empresa_id),
            title=model.title,
            description=model.description,
            location=model.location,
            priority=PriorityLevel(model.priority),
            reported_by=model.reported_by,
            status=ReportStatus(model.status),
            version=model.version,
            created_at=model.created_at,
        )

    async def list_by_company(
        self,
        empresa_id: CompanyId,
        offset: int = 0,
        limit: int = 10,
        filters: dict[str, str] | None = None,
    ) -> tuple[list[FailureReport], int]:
        """Lista los reportes de falla de una empresa con soporte de filtros y paginación.

        Args:
            empresa_id: Identificador de la empresa.
            offset: Número de registros a omitir.
            limit: Número máximo de registros a retornar.
            filters: Diccionario opcional con filtros (status, priority, search).

        Returns:
            Una tupla con la lista de entidades FailureReport y el conteo total.
        """
        stmt = select(FailureReportModel).where(
            FailureReportModel.empresa_id == empresa_id.value
        )
        count_stmt = select(func.count(FailureReportModel.id)).where(
            FailureReportModel.empresa_id == empresa_id.value
        )

        if filters:
            if "status" in filters and filters["status"]:
                stmt = stmt.where(FailureReportModel.status == filters["status"])
                count_stmt = count_stmt.where(
                    FailureReportModel.status == filters["status"]
                )
            if "priority" in filters and filters["priority"]:
                stmt = stmt.where(
                    FailureReportModel.priority == filters["priority"]
                )
                count_stmt = count_stmt.where(
                    FailureReportModel.priority == filters["priority"]
                )
            if "search" in filters and filters["search"]:
                search_term = f"%{filters['search']}%"
                stmt = stmt.where(
                    FailureReportModel.title.ilike(search_term)
                    | FailureReportModel.description.ilike(search_term)
                )
                count_stmt = count_stmt.where(
                    FailureReportModel.title.ilike(search_term)
                    | FailureReportModel.description.ilike(search_term)
                )

        count_res = await self.session.execute(count_stmt)
        total = count_res.scalar_one()

        stmt = stmt.offset(offset).limit(limit).order_by(FailureReportModel.id)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models], total
