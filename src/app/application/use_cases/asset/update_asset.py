from app.application.dtos.asset_dtos import AssetResponse, UpdateAssetRequest
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.enums import AssetStatus
from app.domain.exceptions import (
    AssetCodeExistsError,
    AssetNotFoundError,
    AssetSerialExistsError,
    LocationNotFoundError,
    ValidationException,
)
from app.domain.value_objects import AssetId, CompanyId, LocationId


class UpdateAssetUseCase:
    """Caso de uso para actualizar un activo físico."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        """Inicializa el caso de uso con la unidad de trabajo (UoW)."""
        self.uow = uow

    async def execute(
        self, company_id_str: str, asset_id_str: str, request: UpdateAssetRequest
    ) -> AssetResponse:
        """Ejecuta la actualización del activo físico."""
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
                    asset.ubicacion_id = loc_id
                else:
                    asset.ubicacion_id = None

            if request.codigo_activo is not None:
                new_code = request.codigo_activo.strip()
                if not new_code:
                    raise ValidationException("El código del activo no puede estar vacío.")
                assets, _ = await self.uow.assets.list_by_company(company_id, 0, 1000)
                if any(
                    a.codigo_activo.lower() == new_code.lower() and a.id != asset.id for a in assets
                ):
                    raise AssetCodeExistsError(
                        f"El activo con código '{new_code}' ya existe en esta empresa."
                    )
                asset.codigo_activo = new_code

            if request.serial_interno is not None:
                new_serial = request.serial_interno.strip()
                if not new_serial:
                    raise ValidationException("El serial interno no puede estar vacío.")
                assets, _ = await self.uow.assets.list_by_company(company_id, 0, 1000)
                if any(
                    a.serial_interno.lower() == new_serial.lower() and a.id != asset.id
                    for a in assets
                ):
                    raise AssetSerialExistsError(
                        f"El activo con serial '{new_serial}' ya existe en esta empresa."
                    )
                asset.serial_interno = new_serial

            if request.estado is not None:
                asset.estado = AssetStatus(request.estado)

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
