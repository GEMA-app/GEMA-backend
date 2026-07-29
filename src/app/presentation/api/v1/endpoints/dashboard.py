"""Endpoints REST para el módulo de dashboard (JSON:API).

Proporciona el endpoint de agregación de métricas y KPIs para los dashboards.
"""

import uuid

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func, select

from app.application.dtos.auth_dtos import UserResponse
from app.infrastructure.db.models.asset import AssetModel
from app.infrastructure.db.models.inventory_part import InventoryPartModel
from app.infrastructure.db.models.work_order import WorkOrderModel
from app.infrastructure.db.session import async_session_factory
from app.presentation.api.v1.endpoints.dependencies import require_tenant_read

router = APIRouter()


class DashboardResumenAttributes(BaseModel):
    """Atributos de resumen de KPIs del dashboard."""

    total_activos: int = 0
    activos_operativos: int = 0
    activos_en_mantenimiento: int = 0
    activos_fuera_de_servicio: int = 0
    activos_dados_de_baja: int = 0
    total_ots: int = 0
    ots_abiertas: int = 0
    ots_en_proceso: int = 0
    ots_cerradas: int = 0
    costo_real_acumulado: float = 0.0
    repuestos_bajo_minimo: int = 0


class DashboardResumenResource(BaseModel):
    """Recurso del resumen de KPIs."""

    id: str = "resumen"
    type: str = "dashboard-resumen"
    attributes: DashboardResumenAttributes


class DashboardResumenDocument(BaseModel):
    """Documento de respuesta para el resumen de KPIs."""

    data: DashboardResumenResource


@router.get(
    "/resumen",
    response_model=DashboardResumenDocument,
    summary="Obtener resumen de KPIs para el dashboard",
)
async def get_dashboard_resumen(
    empresa_id: str,
    current_user: UserResponse = Depends(require_tenant_read),
) -> DashboardResumenDocument:
    """Retorna métricas consolidadas de activos, órdenes de trabajo e inventario.

    Se obtienen en una sola consulta.
    """
    empresa_uuid = uuid.UUID(empresa_id)

    async with async_session_factory() as session:
        # 1. Métricas de activos por estado
        asset_stmt = (
            select(AssetModel.estado, func.count(AssetModel.id))
            .where(AssetModel.empresa_id == empresa_uuid)
            .group_by(AssetModel.estado)
        )

        asset_res = await session.execute(asset_stmt)
        asset_counts: dict[str, int] = {}
        total_activos = 0
        for estado_enum, count in asset_res.all():
            st_val = estado_enum.value if hasattr(estado_enum, "value") else str(estado_enum)
            asset_counts[st_val] = count
            total_activos += count

        # 2. Métricas de órdenes de trabajo por estado y costo acumulado
        ot_stmt = (
            select(
                WorkOrderModel.estado,
                func.count(WorkOrderModel.id),
                func.coalesce(func.sum(WorkOrderModel.costo_real), 0),
            )
            .where(WorkOrderModel.empresa_id == empresa_uuid)
            .group_by(WorkOrderModel.estado)
        )

        ot_res = await session.execute(ot_stmt)
        ot_counts: dict[str, int] = {}
        total_ots = 0
        costo_total = 0.0
        for estado_enum, count, sum_cost in ot_res.all():
            st_val = estado_enum.value if hasattr(estado_enum, "value") else str(estado_enum)
            ot_counts[st_val] = count
            total_ots += count
            costo_total += float(sum_cost)

        # 3. Stock crítico (bajo mínimo)
        inv_stmt = select(func.count(InventoryPartModel.id)).where(
            InventoryPartModel.empresa_id == empresa_uuid,
            InventoryPartModel.stock_actual <= InventoryPartModel.stock_minimo,
        )
        inv_res = await session.execute(inv_stmt)
        repuestos_bajo_minimo = inv_res.scalar_one()

    attrs = DashboardResumenAttributes(
        total_activos=total_activos,
        activos_operativos=asset_counts.get("operativo", 0),
        activos_en_mantenimiento=asset_counts.get("en_mantenimiento", 0),
        activos_fuera_de_servicio=asset_counts.get("fuera_de_servicio", 0),
        activos_dados_de_baja=asset_counts.get("dado_de_baja", 0),
        total_ots=total_ots,
        ots_abiertas=ot_counts.get("abierta", 0),
        ots_en_proceso=ot_counts.get("en_proceso", 0),
        ots_cerradas=ot_counts.get("cerrada", 0),
        costo_real_acumulado=round(costo_total, 2),
        repuestos_bajo_minimo=repuestos_bajo_minimo,
    )

    return DashboardResumenDocument(
        data=DashboardResumenResource(
            id=empresa_id,
            attributes=attrs,
        )
    )
