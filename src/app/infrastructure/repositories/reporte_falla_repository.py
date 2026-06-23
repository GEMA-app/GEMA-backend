from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.models.reporte_falla import ReporteFallaModel
from app.domain.entities.reporte_falla import ReporteFalla

class SqlAlchemyReporteFallaRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, entity: ReporteFalla) -> ReporteFalla:
        db_model = ReporteFallaModel(
            id=entity.id,
            titulo=entity.titulo,
            descripcion=entity.descripcion,
            ubicacion=entity.ubicacion,
            prioridad=entity.prioridad,
            reportado_por=entity.reportado_por,
            estado=entity.estado,
            fecha_creacion=entity.fecha_creacion
        )
        
        self.session.add(db_model)
        await self.session.commit()
        await self.session.refresh(db_model)
        
        return entity