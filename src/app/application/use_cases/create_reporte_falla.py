from app.domain.entities.reporte_falla import ReporteFalla

class CreateReporteFallaUseCase:
    def __init__(self, repo):
        self.repo = repo

    async def execute(self, data) -> ReporteFalla:
        # Aquí puedes meter reglas de negocio si hacen falta en el futuro
        nueva_falla = ReporteFalla(
            titulo=data.titulo,
            descripcion=data.descripcion,
            ubicacion=data.ubicacion,
            prioridad=data.prioridad,
            reportado_por=data.reportado_por
        )
        return await self.repo.save(nueva_falla)