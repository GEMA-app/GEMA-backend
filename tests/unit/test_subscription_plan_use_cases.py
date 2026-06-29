"""Tests unitarios para los casos de uso del módulo SubscriptionPlan."""
from decimal import Decimal
from typing import Any
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.application.dtos.subscription_plan_dtos import (
    CreateSubscriptionPlanRequest,
    UpdateSubscriptionPlanRequest,
)
from app.application.use_cases.subscription_plan.create_subscription_plan import (
    CreateSubscriptionPlanUseCase,
)
from app.application.use_cases.subscription_plan.delete_subscription_plan import (
    DeleteSubscriptionPlanUseCase,
)
from app.application.use_cases.subscription_plan.get_subscription_plan import (
    GetSubscriptionPlanUseCase,
)
from app.application.use_cases.subscription_plan.list_subscription_plans import (
    ListSubscriptionPlansUseCase,
)
from app.application.use_cases.subscription_plan.update_subscription_plan import (
    UpdateSubscriptionPlanUseCase,
)
from app.domain.entities.subscription_plan import SubscriptionPlan
from app.domain.exceptions.subscription_plan import (
    SubscriptionPlanAlreadyExistsError,
    SubscriptionPlanHasActiveSubscriptionsError,
    SubscriptionPlanInvalidDataError,
    SubscriptionPlanNotFoundError,
)


@pytest.fixture
def mock_uow() -> Any:
    uow = MagicMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)
    uow.subscription_plans = MagicMock()
    uow.subscription_plans.get_by_id = AsyncMock()
    uow.subscription_plans.get_by_name = AsyncMock()
    uow.subscription_plans.save = AsyncMock()
    uow.subscription_plans.delete = AsyncMock()
    uow.subscription_plans.list_all_plans = AsyncMock()
    uow.companies = MagicMock()
    uow.companies.count_by_plan_id = AsyncMock()
    uow.commit = AsyncMock()
    return uow


class TestCreateSubscriptionPlanUseCase:

    async def test_create_plan_success(self, mock_uow: Any) -> None:
        mock_uow.subscription_plans.get_by_name.return_value = None
        use_case = CreateSubscriptionPlanUseCase(uow=mock_uow)

        dto = CreateSubscriptionPlanRequest(
            nombre="Plan Básico",
            descripcion="Descripción del plan básico",
            precio_mensual_usd=Decimal("19.99"),
            max_activos=100,
            max_usuarios=10,
        )

        response = await use_case.execute(dto)

        assert response.nombre == "Plan Básico"
        assert response.precio_mensual_usd == Decimal("19.99")
        assert response.max_activos == 100
        assert response.max_usuarios == 10
        assert response.is_active is True
        mock_uow.subscription_plans.save.assert_called_once()
        mock_uow.commit.assert_called_once()

    async def test_create_plan_duplicate_name_raises_error(self, mock_uow: Any) -> None:
        existing_plan = SubscriptionPlan.create(
            nombre="Plan Básico",
            descripcion="Existing",
            max_activos=10,
            max_usuarios=2,
            precio_mensual_usd=Decimal("9.99"),
        )
        mock_uow.subscription_plans.get_by_name.return_value = existing_plan
        use_case = CreateSubscriptionPlanUseCase(uow=mock_uow)

        dto = CreateSubscriptionPlanRequest(
            nombre="Plan Básico",
            descripcion="Descripción",
            precio_mensual_usd=Decimal("19.99"),
            max_activos=100,
            max_usuarios=10,
        )

        with pytest.raises(SubscriptionPlanAlreadyExistsError) as exc_info:
            await use_case.execute(dto)

        assert "Ya existe un plan de suscripción con el nombre" in str(exc_info.value)
        mock_uow.subscription_plans.save.assert_not_called()


class TestGetSubscriptionPlanUseCase:

    async def test_get_plan_success(self, mock_uow: Any) -> None:
        plan = SubscriptionPlan.create(
            nombre="Plan Premium",
            descripcion="Premium desc",
            max_activos=500,
            max_usuarios=50,
            precio_mensual_usd=Decimal("49.99"),
        )
        mock_uow.subscription_plans.get_by_id.return_value = plan
        use_case = GetSubscriptionPlanUseCase(uow=mock_uow)

        response = await use_case.execute(str(plan.id))

        assert response.id == str(plan.id)
        assert response.nombre == "Plan Premium"
        assert response.max_activos == 500

    async def test_get_plan_not_found_raises_error(self, mock_uow: Any) -> None:
        mock_uow.subscription_plans.get_by_id.return_value = None
        use_case = GetSubscriptionPlanUseCase(uow=mock_uow)
        plan_id = str(uuid4())

        with pytest.raises(SubscriptionPlanNotFoundError) as exc_info:
            await use_case.execute(plan_id)

        assert f"El plan de suscripción con ID '{plan_id}' no existe." in str(exc_info.value)


class TestListSubscriptionPlansUseCase:

    async def test_list_plans_success(self, mock_uow: Any) -> None:
        plan = SubscriptionPlan.create(
            nombre="Plan Premium",
            descripcion="Premium desc",
            max_activos=500,
            max_usuarios=50,
            precio_mensual_usd=Decimal("49.99"),
        )
        mock_uow.subscription_plans.list_all_plans.return_value = ([plan], 1)
        use_case = ListSubscriptionPlansUseCase(uow=mock_uow)

        plans, total = await use_case.execute(offset=0, limit=10)

        assert len(plans) == 1
        assert total == 1
        assert plans[0].nombre == "Plan Premium"
        mock_uow.subscription_plans.list_all_plans.assert_called_once_with(0, 10)


class TestUpdateSubscriptionPlanUseCase:

    async def test_update_plan_success(self, mock_uow: Any) -> None:
        plan = SubscriptionPlan.create(
            nombre="Plan Original",
            descripcion="Original desc",
            max_activos=10,
            max_usuarios=2,
            precio_mensual_usd=Decimal("9.99"),
        )
        mock_uow.subscription_plans.get_by_id.return_value = plan
        use_case = UpdateSubscriptionPlanUseCase(uow=mock_uow)

        dto = UpdateSubscriptionPlanRequest(
            nombre="Plan Actualizado",
            descripcion="Nueva descripción",
            precio_mensual_usd=Decimal("15.00"),
            max_activos=20,
            max_usuarios=5,
            is_active=False,
        )

        response = await use_case.execute(str(plan.id), dto)

        assert response.nombre == "Plan Actualizado"
        assert response.descripcion == "Nueva descripción"
        assert response.precio_mensual_usd == Decimal("15.00")
        assert response.max_activos == 20
        assert response.max_usuarios == 5
        assert response.is_active is False
        mock_uow.commit.assert_called_once()

    async def test_update_plan_invalid_price_raises_error(self, mock_uow: Any) -> None:
        plan = SubscriptionPlan.create(
            nombre="Plan Original",
            descripcion="Original desc",
            max_activos=10,
            max_usuarios=2,
            precio_mensual_usd=Decimal("9.99"),
        )
        mock_uow.subscription_plans.get_by_id.return_value = plan
        use_case = UpdateSubscriptionPlanUseCase(uow=mock_uow)

        dto = UpdateSubscriptionPlanRequest(
            nombre="Plan Actualizado",
            descripcion="Nueva descripción",
            precio_mensual_usd=Decimal("-5.00"),
            max_activos=20,
            max_usuarios=5,
            is_active=True,
        )

        with pytest.raises(SubscriptionPlanInvalidDataError) as exc_info:
            await use_case.execute(str(plan.id), dto)

        assert "El precio mensual no puede ser negativo" in str(exc_info.value)

    async def test_update_plan_empty_name_raises_error(self, mock_uow: Any) -> None:
        plan = SubscriptionPlan.create(
            nombre="Plan Original",
            descripcion="Original desc",
            max_activos=10,
            max_usuarios=2,
            precio_mensual_usd=Decimal("9.99"),
        )
        mock_uow.subscription_plans.get_by_id.return_value = plan
        use_case = UpdateSubscriptionPlanUseCase(uow=mock_uow)

        dto = UpdateSubscriptionPlanRequest(
            nombre="   ",
            descripcion="Nueva descripción",
            precio_mensual_usd=Decimal("15.00"),
            max_activos=20,
            max_usuarios=5,
            is_active=True,
        )

        with pytest.raises(SubscriptionPlanInvalidDataError) as exc_info:
            await use_case.execute(str(plan.id), dto)

        assert "El nombre del plan no puede estar vacío" in str(exc_info.value)


class TestDeleteSubscriptionPlanUseCase:

    async def test_delete_plan_success(self, mock_uow: Any) -> None:
        plan = SubscriptionPlan.create(
            nombre="Plan Temp",
            descripcion="Temp",
            max_activos=10,
            max_usuarios=2,
            precio_mensual_usd=Decimal("9.99"),
        )
        mock_uow.subscription_plans.get_by_id.return_value = plan
        mock_uow.companies.count_by_plan_id.return_value = 0
        use_case = DeleteSubscriptionPlanUseCase(uow=mock_uow)

        await use_case.execute(str(plan.id))

        mock_uow.subscription_plans.delete.assert_called_once_with(plan.id)
        mock_uow.commit.assert_called_once()

    async def test_delete_plan_with_companies_raises_conflict_error(self, mock_uow: Any) -> None:
        plan = SubscriptionPlan.create(
            nombre="Plan Conectado",
            descripcion="Tiene empresas",
            max_activos=10,
            max_usuarios=2,
            precio_mensual_usd=Decimal("9.99"),
        )
        mock_uow.subscription_plans.get_by_id.return_value = plan
        # Simular que hay 3 empresas asociadas a este plan
        mock_uow.companies.count_by_plan_id.return_value = 3
        use_case = DeleteSubscriptionPlanUseCase(uow=mock_uow)

        with pytest.raises(SubscriptionPlanHasActiveSubscriptionsError) as exc_info:
            await use_case.execute(str(plan.id))

        assert "No se puede eliminar el plan 'Plan Conectado' porque está asignado a 3 empresa(s)" in str(exc_info.value)
        mock_uow.subscription_plans.delete.assert_not_called()
        mock_uow.commit.assert_not_called()
