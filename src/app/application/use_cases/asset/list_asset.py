"""Caso de uso para list asset."""
from typing import Any

from app.application.dtos.asset_dtos import AssetResponse
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.value_objects import CompanyId


class ListAssetsUseCase:
    """Caso de uso para listar los activos de una empresa con soporte para paginación y filtros."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(
        self, company_id_str: str, offset: int, limit: int, filters: dict[str, Any] | None = None
    ) -> tuple[list[AssetResponse], int]:
        """Lista los activos de una empresa con paginación y filtros."""
        company_id = CompanyId.from_string(company_id_str)
        async with self.uow:
            assets, total = await self.uow.assets.list_by_company(
                company_id, offset, limit, filters
            )
            responses = [
                AssetResponse(
                    id=str(a.id),
                    empresa_id=str(a.empresa_id),
                    articulo_id=str(a.articulo_id),
                    ubicacion_id=str(a.ubicacion_id) if a.ubicacion_id else None,
                    serial_interno=a.serial_interno,
                    codigo_activo=a.codigo_activo,
                    estado=a.estado.value,
                    fecha_adquisicion=a.fecha_adquisicion.isoformat()
                    if a.fecha_adquisicion
                    else None,
                    valor_monetario=(
                        float(a.valor_monetario)
                        if a.valor_monetario is not None
                        else None
                    ),
                    moneda=a.moneda,
                    version=a.version,
                )
                for a in assets
            ]
            return responses, total
