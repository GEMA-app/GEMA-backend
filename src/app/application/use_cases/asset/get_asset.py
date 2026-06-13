from app.application.dtos.asset_dtos import AssetResponse
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.exceptions import AssetNotFoundError
from app.domain.value_objects import AssetId, CompanyId


class GetAssetUseCase:
    """Caso de uso para obtener un activo por su ID."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(self, company_id_str: str, asset_id_str: str) -> AssetResponse:
        """Obtiene un activo por su ID."""
        company_id = CompanyId.from_string(company_id_str)
        asset_id = AssetId.from_string(asset_id_str)

        async with self.uow:
            asset = await self.uow.assets.get_by_id(asset_id, company_id)
            if not asset:
                raise AssetNotFoundError(
                    f"El activo con ID '{asset_id_str}' no existe en esta empresa."
                )

            return AssetResponse(
                id=str(asset.id),
                empresa_id=str(asset.empresa_id),
                articulo_id=str(asset.articulo_id),
                ubicacion_id=str(asset.ubicacion_id) if asset.ubicacion_id else None,
                serial_interno=asset.serial_interno,
                codigo_activo=asset.codigo_activo,
                estado=asset.estado.value,
                fecha_adquisicion=asset.fecha_adquisicion.isoformat()
                if asset.fecha_adquisicion
                else None,
                valor_monetario=asset.valor_monetario,
                moneda=asset.moneda,
                version=asset.version,
            )
