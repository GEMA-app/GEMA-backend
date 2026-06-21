from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

# Inyección de la base de datos
from app.infrastructure.db.session import get_db 
# El modelo ORM que creamos juntas
from app.infrastructure.db.models.asset_state_log import AssetStateLogModel
# El DTO que creamos en el paso anterior
from app.application.dtos.asset_state_log_dtos import AssetStateLogResponse

router = APIRouter()

@router.get(
    "/empresas/{empresa_id}/activos/{activo_id}/historial-estados",
    response_model=List[AssetStateLogResponse],
    status_code=status.HTTP_200_OK,
    summary="Trazabilidad de estados del activo"
)
def get_asset_state_history(
    empresa_id: UUID,
    activo_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Retorna la lista ordenada cronológicamente de los cambios de estado de un activo específico.
    """
    logs = (
        db.query(AssetStateLogModel)
        .filter(AssetStateLogModel.activo_id == activo_id)
        .order_by(AssetStateLogModel.fecha_cambio.desc())
        .all()
    )
    return logs