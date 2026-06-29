"""Casos de uso del módulo UsedPart."""

from app.application.use_cases.used_part.create_used_part import CreateUsedPartUseCase
from app.application.use_cases.used_part.delete_used_part import DeleteUsedPartUseCase
from app.application.use_cases.used_part.get_used_part import GetUsedPartUseCase
from app.application.use_cases.used_part.list_used_part import ListUsedPartsUseCase
from app.application.use_cases.used_part.update_used_part import UpdateUsedPartUseCase

__all__ = [
    "CreateUsedPartUseCase",
    "DeleteUsedPartUseCase",
    "GetUsedPartUseCase",
    "ListUsedPartsUseCase",
    "UpdateUsedPartUseCase",
]
