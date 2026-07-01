"""Caso de uso para update asset."""

import uuid
from datetime import UTC, datetime
from decimal import Decimal

from app.application.dtos.asset_dtos import AssetResponse, UpdateAssetRequest
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.entities import AssetStateLog
from app.domain.enums import AssetStatus
from app.domain.exceptions import (
    AssetNotFoundError,
    LocationNotFoundError,
    StaleDataError,
    ValidationException,
)
from app.domain.value_objects import AssetId, CompanyId, LocationId


class UpdateAssetUseCase:
    """Actualiza un activo físico de la empresa."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        """Guarda dependencias."""
        self.uow = uow

    async def execute(
        self,
        company_id_str: str,
        asset_id_str: str,
        request: UpdateAssetRequest,
        usuario_id_str: str | None = None,
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

            if request.version is not None and request.version != asset.version:
                raise StaleDataError(
                    f"Conflicto de versión para activo: se esperaba {request.version}, "
                    f"la actual es {asset.version}."
                )

            if "ubicacion_id" in request._fields_set:
                if request.ubicacion_id is not None:
                    u_id_str = request.ubicacion_id.strip()
                    if not u_id_str:
                        raise ValidationException("El ID de la ubicación no puede estar vacío.")
                    loc_id = LocationId.from_string(u_id_str)
                    loc = await self.uow.locations.get_by_id(loc_id, company_id)
                    if not loc:
                        raise LocationNotFoundError(f"La ubicación con ID '{u_id_str}' no existe.")
                    asset.transfer_location(loc_id)
                else:
                    asset.transfer_location(None)

            if "codigo_activo" in request._fields_set:
                if request.codigo_activo is None:
                    raise ValidationException("El código del activo no puede ser nulo.")
                new_code = request.codigo_activo.lower().strip()
                if not new_code:
                    raise ValidationException("El código del activo no puede estar vacío.")
                asset.codigo_activo = new_code

            if "serial_interno" in request._fields_set:
                if request.serial_interno is None:
                    raise ValidationException("El serial interno no puede ser nulo.")
                new_serial = request.serial_interno.lower().strip()
                if not new_serial:
                    raise ValidationException("El serial interno no puede estar vacío.")
                asset.serial_interno = new_serial

            state_changed = False
            old_status = asset.estado
            if "estado" in request._fields_set:
                if request.estado is None:
                    raise ValidationException("El estado no puede ser nulo.")
                estado_destino = AssetStatus(request.estado)
                if estado_destino != old_status:
                    state_changed = True
                    if estado_destino == AssetStatus.UNDER_MAINTENANCE:
                        asset.mark_as_under_maintenance()
                    elif estado_destino == AssetStatus.DECOMMISSIONED:
                        asset.decommission()
                    elif estado_destino == AssetStatus.OPERATIONAL:
                        asset.put_in_service()
                    elif estado_destino == AssetStatus.OUT_OF_SERVICE:
                        asset.take_out_of_service()

            if "fecha_adquisicion" in request._fields_set:
                asset.fecha_adquisicion = request.fecha_adquisicion

            if "valor_monetario" in request._fields_set:
                asset.valor_monetario = (
                    Decimal(request.valor_monetario)
                    if request.valor_monetario is not None
                    else None
                )

            if "moneda" in request._fields_set:
                if request.moneda is None:
                    raise ValidationException("La moneda no puede ser nula.")
                asset.moneda = request.moneda

            await self.uow.assets.save(asset)

            if state_changed:
                log_entry = AssetStateLog(
                    id=uuid.uuid4(),
                    empresa_id=company_id,
                    activo_id=asset.id,
                    estado_anterior=old_status,
                    estado_nuevo=asset.estado,
                    motivo=None,
                    fecha_cambio=datetime.now(UTC),
                    usuario_id=uuid.UUID(usuario_id_str) if usuario_id_str else None,
                )
                await self.uow.asset_state_logs.save(log_entry)

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
                valor_monetario=(
                    float(asset.valor_monetario) if asset.valor_monetario is not None else None
                ),
                moneda=asset.moneda,
                version=asset.version,
            )
