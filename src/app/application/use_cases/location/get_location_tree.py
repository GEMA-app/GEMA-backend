"""Caso de uso para get location tree."""

from typing import Any

import structlog

from app.application.dtos.location_dtos import LocationTreeResponse
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.value_objects import CompanyId

logger = structlog.get_logger()


class GetLocationTreeUseCase:
    """Reconstruye y retorna el árbol jerárquico de ubicaciones de una empresa."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(self, company_id_str: str) -> list[LocationTreeResponse]:
        """Reconstruye y retorna el árbol jerárquico de ubicaciones."""
        company_id = CompanyId.from_string(company_id_str)

        async with self.uow:
            locations = await self.uow.locations.get_tree(company_id)

            # Construir mapa de id -> nodo diccionario
            nodes: dict[str, dict[str, Any]] = {
                str(loc.id): {
                    "id": str(loc.id),
                    "nombre": loc.nombre,
                    "tipo": loc.tipo.value,
                    "descripcion": loc.descripcion,
                    "parent_id": str(loc.parent_id) if loc.parent_id else None,
                    "children": [],
                }
                for loc in locations
            }

            roots: list[dict[str, Any]] = []
            for loc in locations:
                node = nodes[str(loc.id)]
                if loc.parent_id:
                    pid_str = str(loc.parent_id)
                    if pid_str in nodes:
                        nodes[pid_str]["children"].append(node)
                    else:
                        logger.warning(
                            "orphan_location_detected",
                            location_id=str(loc.id),
                            parent_id=pid_str,
                        )
                        roots.append(node)  # Promover a raiz para visibilidad
                else:
                    roots.append(node)

            # Convertir diccionarios recursivamente a DTOs de árbol
            def to_dto(n: dict[str, Any], visited: set[str] | None = None) -> LocationTreeResponse:
                if visited is None:
                    visited = set()
                if n["id"] in visited:
                    logger.error("cycle_detected_in_location_tree", location_id=n["id"])
                    return LocationTreeResponse(
                        id=n["id"],
                        nombre=n["nombre"],
                        tipo=n["tipo"],
                        descripcion=n["descripcion"],
                        children=[],
                    )
                visited.add(n["id"])
                return LocationTreeResponse(
                    id=n["id"],
                    nombre=n["nombre"],
                    tipo=n["tipo"],
                    descripcion=n["descripcion"],
                    children=[to_dto(c, visited.copy()) for c in n["children"]],
                )

            return [to_dto(r) for r in roots]
