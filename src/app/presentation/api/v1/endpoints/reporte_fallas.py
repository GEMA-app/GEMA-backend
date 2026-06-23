from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.presentation.api.v1.dependencies import get_db
from app.presentation.schemas.reporte_falla import ReporteFallaCreate
from app.application.use_cases.create_reporte_falla import CreateReporteFallaUseCase
from app.infrastructure.repositories.reporte_falla_repository import SqlAlchemyReporteFallaRepository

router = APIRouter(prefix="/reporte-fallas", tags=["Reporte de Fallas"])

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_reporte_falla(
    data: ReporteFallaCreate,
    db: AsyncSession = Depends(get_db)
):
    repo = SqlAlchemyReporteFallaRepository(db)
    use_case = CreateReporteFallaUseCase(repo)
    nueva_falla = await use_case.execute(data)
    
    return {
        "message": "Reporte de falla registrado con éxito",
        "id": nueva_falla.id,
        "estado": nueva_falla.estado
    }