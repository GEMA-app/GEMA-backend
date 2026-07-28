from typing import Any
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.application.dtos.location_dtos import UpdateLocationRequest
from app.application.use_cases.location.update_location import UpdateLocationUseCase
from app.domain.entities import Location
from app.domain.enums import LocationType
from app.domain.exceptions import ValidationException
from app.domain.value_objects import CompanyId, LocationId


@pytest.fixture
def mock_uow() -> Any:
    uow = MagicMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)
    uow.locations = MagicMock()
    uow.locations.get_by_id = AsyncMock()
    uow.locations.get_children = AsyncMock()
    uow.locations.save = AsyncMock()
    uow.commit = AsyncMock()
    return uow


class TestUpdateLocationUseCaseDescendants:

    async def test_update_location_type_change_invalidates_child_raises_validation_exception(self, mock_uow: Any) -> None:
        company_id = CompanyId(uuid4())
        location_id = LocationId(uuid4())

        # Simular ubicacion B de tipo PLANT
        location_b = Location(
            id=location_id,
            empresa_id=company_id,
            parent_id=LocationId(uuid4()),
            nombre="Planta B",
            tipo=LocationType.PLANT,
            descripcion="Planta"
        )
        mock_uow.locations.get_by_id.side_effect = lambda lid, cid: (
            location_b if lid == location_id else None
        )

        # Simular hijo C de tipo AREA
        location_c = Location(
            id=LocationId(uuid4()),
            empresa_id=company_id,
            parent_id=location_id,
            nombre="Area C",
            tipo=LocationType.AREA,
            descripcion="Area"
        )
        mock_uow.locations.get_children.return_value = [location_c]

        use_case = UpdateLocationUseCase(uow=mock_uow)

        # Intentamos cambiar B a HEADQUARTERS.
        # HEADQUARTERS no permite hijos de tipo AREA directamente (AREA requiere PLANT).
        request = UpdateLocationRequest(
            tipo=LocationType.HEADQUARTERS.value,
            _fields_set=frozenset(["tipo"])
        )

        with pytest.raises(ValidationException) as exc_info:
            await use_case.execute(str(company_id.value), str(location_id.value), request)

        assert "invalida la ubicación hija" in str(exc_info.value)
        mock_uow.locations.save.assert_not_called()


class TestDeleteLocationUseCaseCascade:

    async def test_delete_location_deletes_children_in_cascade(self, mock_uow: Any) -> None:
        from app.application.use_cases.location.delete_location import DeleteLocationUseCase

        company_id = CompanyId(uuid4())
        parent_id = LocationId(uuid4())
        child_id = LocationId(uuid4())

        parent_loc = Location(
            id=parent_id,
            empresa_id=company_id,
            parent_id=None,
            nombre="Sede Principal",
            tipo=LocationType.HEADQUARTERS,
        )
        child_loc = Location(
            id=child_id,
            empresa_id=company_id,
            parent_id=parent_id,
            nombre="Planta 1",
            tipo=LocationType.PLANT,
        )

        mock_uow.locations.get_by_id.return_value = parent_loc
        mock_uow.locations.get_children.side_effect = lambda lid, cid: (
            [child_loc] if lid == parent_id else []
        )
        mock_uow.locations.delete = AsyncMock()

        use_case = DeleteLocationUseCase(uow=mock_uow)
        await use_case.execute(str(company_id.value), str(parent_id.value))

        # Verifica borrado de la hija primero y luego de la padre
        assert mock_uow.locations.delete.call_count == 2
        mock_uow.locations.delete.assert_any_call(child_id, company_id)
        mock_uow.locations.delete.assert_any_call(parent_id, company_id)

