"""Casos de uso del módulo de activos físicos."""

from app.application.use_cases.asset.create_asset import CreateAssetUseCase
from app.application.use_cases.asset.delete_asset import DeleteAssetUseCase
from app.application.use_cases.asset.get_asset import GetAssetUseCase
from app.application.use_cases.asset.list_asset import ListAssetsUseCase
from app.application.use_cases.asset.update_asset import UpdateAssetUseCase

__all__ = [
    "CreateAssetUseCase",
    "GetAssetUseCase",
    "ListAssetsUseCase",
    "UpdateAssetUseCase",
    "DeleteAssetUseCase",
]
