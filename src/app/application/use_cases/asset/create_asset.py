import uuid

from app.application.dtos.asset_dtos import AssetResponse, CreateAssetRequest
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.entities import Asset
from app.domain.enums import AssetStatus
from app.domain.exceptions import (
    AssetCodeExistsError,
    AssetSerialExistsError,
    LocationNotFoundError,
)
from app.domain.value_objects import AssetId, CompanyId, LocationId


class CreateAssetUseCase:
    """Caso de uso para registrar un nuevo activo físico en la empresa."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(self, company_id_str: str, request: CreateAssetRequest) -> AssetResponse:
        company_id = CompanyId.from_string(company_id_str)

        async with self.uow:
            # Validar ubicación si se proporciona
            if request.ubicacion_id:
                loc_id = LocationId.from_string(request.ubicacion_id)
                loc = await self.uow.locations.get_by_id(loc_id, company_id)
                if not loc:
                    raise LocationNotFoundError(f"La ubicación con ID '{request.ubicacion_id}' no existe.")
            else:
                loc_id = None

            # Verificar duplicados de código o serial en la misma empresa
            assets, _ = await self.uow.assets.list_by_company(company_id, 0, 1000)
            if any(a.codigo_activo.lower() == request.codigo_activo.strip().lower() for a in assets):
                raise AssetCodeExistsError(
                    f"El activo con código '{request.codigo_activo}' ya existe en esta empresa."
                )
            if any(a.serial_interno.lower() == request.serial_interno.strip().lower() for a in assets):
                raise AssetSerialExistsError(
                    f"El activo con serial '{request.serial_interno}' ya existe en esta empresa."
                )

            asset = Asset(
                id=AssetId(uuid.uuid4()),
                empresa_id=company_id,
                articulo_id=uuid.UUID(request.articulo_id),
                ubicacion_id=loc_id,
                serial_interno=request.serial_interno.strip(),
                codigo_activo=request.codigo_activo.strip(),
                estado=AssetStatus(request.estado),
                fecha_adquisicion=request.fecha_adquisicion,
                valor_monetario=request.valor_monetario,
                moneda=request.moneda
            )

            await self.uow.assets.save(asset)
            await self.uow.commit()

            return AssetResponse(
                id=str(asset.id),
                empresa_id=str(asset.empresa_id),
                articulo_id=str(asset.articulo_id),
                ubicacion_id=str(asset.ubicacion_id) if asset.ubicacion_id else None,
                serial_interno=asset.serial_interno,
                codigo_activo=asset.codigo_activo,
                estado=asset.estado.value,
                fecha_adquisicion=asset.fecha_adquisicion.isoformat() if asset.fecha_adquisicion else None,
                valor_monetario=asset.valor_monetario,
                moneda=asset.moneda
            )
