"""Caso de uso para delete asset."""

from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.events import AssetDeleted
from app.domain.exceptions import AssetNotFoundError
from app.domain.value_objects import AssetId, CompanyId


class DeleteAssetUseCase:
    """Caso de uso para eliminar un activo."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(self, company_id_str: str, asset_id_str: str) -> None:
        """Elimina un activo por su ID."""
        company_id = CompanyId.from_string(company_id_str)
        asset_id = AssetId.from_string(asset_id_str)

        async with self.uow:
            asset = await self.uow.assets.get_by_id(asset_id, company_id)
            if not asset:
                raise AssetNotFoundError(
                    f"El activo con ID '{asset_id_str}' no existe en esta empresa."
                )

            await self.uow.assets.delete(asset_id, company_id)
            self.uow.add_event(
                AssetDeleted(
                    asset_id=asset_id_str,
                    codigo_activo=asset.codigo_activo,
                    empresa_id=company_id_str,
                )
            )
            await self.uow.commit()
