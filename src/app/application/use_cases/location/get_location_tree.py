from typing import Any

from app.application.dtos.location_dtos import LocationTreeResponse
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.value_objects import CompanyId


class GetLocationTreeUseCase:
    """Caso de uso para reconstruir y retornar el árbol jerárquico de ubicaciones de una empresa."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(self, company_id_str: str) -> list[LocationTreeResponse]:
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
                    roots.append(node)

            # Convertir diccionarios recursivamente a DTOs de árbol
            def to_dto(n: dict[str, Any]) -> LocationTreeResponse:
                return LocationTreeResponse(
                    id=n["id"],
                    nombre=n["nombre"],
                    tipo=n["tipo"],
                    descripcion=n["descripcion"],
                    children=[to_dto(c) for c in n["children"]],
                )

            return [to_dto(r) for r in roots]
