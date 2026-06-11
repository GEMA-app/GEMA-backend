from app.application.dtos.asset_dtos import AssetResponse, UpdateAssetRequest
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.enums import AssetStatus
from app.domain.exceptions import (
    AssetNotFoundError,
    LocationNotFoundError,
    ValidationException,
)
from app.domain.value_objects import AssetId, CompanyId, LocationId


class UpdateAssetUseCase:
    """Actualiza un activo físico de la empresa."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        """Guarda dependencias."""
        self.uow = uow

    async def execute(
        self, company_id_str: str, asset_id_str: str, request: UpdateAssetRequest
    ) -> AssetResponse:
        """Actualiza los datos del activo."""
        company_id = CompanyId.from_string(company_id_str)
        asset_id = AssetId.from_string(asset_id_str)

        async with self.uow:
            asset = await self.uow.assets.get_by_id(asset_id, company_id)
            if not asset:
                raise AssetNotFoundError(
                    f"El activo con ID '{asset_id_str}' no existe en esta empresa."
                )

            if request.ubicacion_id is not None:
                if request.ubicacion_id:
                    loc_id = LocationId.from_string(request.ubicacion_id)
                    loc = await self.uow.locations.get_by_id(loc_id, company_id)
                    if not loc:
                        raise LocationNotFoundError(
                            f"La ubicación con ID '{request.ubicacion_id}' no existe."
                        )
                    asset.transfer_location(loc_id)
                else:
                    asset.ubicacion_id = None

            if request.codigo_activo is not None:
                new_code = request.codigo_activo.lower().strip()
                if not new_code:
                    raise ValidationException("El código del activo no puede estar vacío.")
                asset.codigo_activo = new_code

            if request.serial_interno is not None:
                new_serial = request.serial_interno.lower().strip()
                if not new_serial:
                    raise ValidationException("El serial interno no puede estar vacío.")
                asset.serial_interno = new_serial

            if request.estado is not None:
                estado_destino = AssetStatus(request.estado)
                if estado_destino == AssetStatus.UNDER_MAINTENANCE:
                    asset.mark_as_under_maintenance()
                elif estado_destino == AssetStatus.DECOMMISSIONED:
                    asset.decommission()
                elif estado_destino == AssetStatus.OPERATIONAL:
                    asset.put_in_service()
                elif estado_destino == AssetStatus.OUT_OF_SERVICE:
                    asset.take_out_of_service()

            if request.fecha_adquisicion is not None:
                asset.fecha_adquisicion = request.fecha_adquisicion

            if request.valor_monetario is not None:
                asset.valor_monetario = request.valor_monetario

            if request.moneda is not None:
                asset.moneda = request.moneda

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
                fecha_adquisicion=asset.fecha_adquisicion.isoformat()
                if asset.fecha_adquisicion
                else None,
                valor_monetario=asset.valor_monetario,
                moneda=asset.moneda,
            )
