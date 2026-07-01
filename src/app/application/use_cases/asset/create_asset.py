"""Caso de uso para create asset."""

import uuid
from datetime import UTC, datetime
from decimal import Decimal

from app.application.dtos.asset_dtos import AssetResponse, CreateAssetRequest
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.entities import Asset, AssetStateLog
from app.domain.enums import AssetStatus
from app.domain.exceptions import (
    LocationNotFoundError,
)
from app.domain.value_objects import CompanyId, LocationId


class CreateAssetUseCase:
    """Caso de uso para registrar un nuevo activo físico en la empresa."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(
        self, company_id_str: str, request: CreateAssetRequest, usuario_id_str: str | None = None
    ) -> AssetResponse:
        """Crea un activo y lo persiste."""
        company_id = CompanyId.from_string(company_id_str)

        async with self.uow:
            # Validar ubicación si se proporciona
            if request.ubicacion_id:
                loc_id = LocationId.from_string(request.ubicacion_id)
                loc = await self.uow.locations.get_by_id(loc_id, company_id)
                if not loc:
                    raise LocationNotFoundError(
                        f"La ubicación con ID '{request.ubicacion_id}' no existe."
                    )
            else:
                loc_id = None

            # Nota: La validación de unicidad case-insensitive se delega al
            # índice funcional LOWER() en PostgreSQL. Si hay violación, el
            # IntegrityError handler la captura y responde con 409 Conflict.

            asset = Asset.create(
                empresa_id=company_id,
                articulo_id=uuid.UUID(request.articulo_id),
                ubicacion_id=loc_id,
                serial_interno=request.serial_interno.lower().strip(),
                codigo_activo=request.codigo_activo.lower().strip(),
                estado=AssetStatus(request.estado),
                fecha_adquisicion=request.fecha_adquisicion,
                valor_monetario=(
                    Decimal(request.valor_monetario)
                    if request.valor_monetario is not None
                    else None
                ),
                moneda=request.moneda,
            )

            await self.uow.assets.save(asset)

            log_entry = AssetStateLog(
                id=uuid.uuid4(),
                empresa_id=company_id,
                activo_id=asset.id,
                estado_anterior=None,
                estado_nuevo=asset.estado,
                motivo="Registro inicial del activo",
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
