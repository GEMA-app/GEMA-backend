"""Casos de uso del módulo de ubicaciones.

Nota: No existe un caso de uso `list_location` porque las ubicaciones
se exponen mediante el árbol jerárquico completo (`GetLocationTreeUseCase`)
y la consulta de hijos directos (`GetLocationChildrenUseCase`), en lugar de
una lista plana sin contexto de jerarquía.
"""
from app.application.use_cases.location.create_location import CreateLocationUseCase
from app.application.use_cases.location.delete_location import DeleteLocationUseCase
from app.application.use_cases.location.get_location import GetLocationUseCase
from app.application.use_cases.location.get_location_children import GetLocationChildrenUseCase
from app.application.use_cases.location.get_location_tree import GetLocationTreeUseCase
from app.application.use_cases.location.update_location import UpdateLocationUseCase

__all__ = [
    "CreateLocationUseCase",
    "GetLocationUseCase",
    "GetLocationTreeUseCase",
    "GetLocationChildrenUseCase",
    "UpdateLocationUseCase",
    "DeleteLocationUseCase",
]
