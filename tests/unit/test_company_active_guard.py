from typing import Any
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.application.dtos.auth_dtos import (
    GetCurrentUserRequest,
    LoginUserRequest,
    RefreshTokenRequest,
)
from app.application.use_cases.auth.get_current_user import GetCurrentUserUseCase
from app.application.use_cases.auth.login_user import LoginUserUseCase
from app.application.use_cases.auth.refresh_token import RefreshTokenUseCase
from app.domain.enums import CompanyStatus
from app.domain.exceptions import UserInactiveError
from app.domain.value_objects import CompanyId, UserId


@pytest.fixture
def mock_uow() -> Any:
    uow = MagicMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)

    uow.users = MagicMock()
    uow.users.get_by_id = AsyncMock()
    uow.users.get_by_email = AsyncMock()
    uow.users.save = AsyncMock()

    uow.companies = MagicMock()
    uow.companies.get_by_id = AsyncMock()

    uow.commit = AsyncMock()
    return uow


@pytest.fixture
def mock_token_service() -> Any:
    token_service = MagicMock()
    token_service.decode_token = AsyncMock()
    token_service.generate_access_token = AsyncMock()
    token_service.generate_refresh_token = AsyncMock()
    token_service.revoke_token = AsyncMock()
    token_service.claim_token = AsyncMock(return_value=True)
    return token_service


@pytest.fixture
def mock_hasher() -> Any:
    hasher = MagicMock()
    hasher.verify = MagicMock(return_value=True)
    return hasher


class TestCompanyActiveGuard:

    async def test_get_current_user_raises_inactive_error_when_company_not_active(self, mock_uow: Any, mock_token_service: Any) -> None:
        user_id = UserId(uuid4())
        company_id = CompanyId(uuid4())

        # Mock token service decode
        mock_token_service.decode_token.return_value = {
            "type": "access",
            "sub": str(user_id.value)
        }

        # Mock user
        mock_user = MagicMock()
        mock_user.id = user_id
        mock_user.empresa_id = company_id
        mock_user.activo = True
        mock_uow.users.get_by_id.return_value = mock_user

        # Mock company suspended
        mock_company = MagicMock()
        mock_company.estado = CompanyStatus.SUSPENDED
        mock_uow.companies.get_by_id.return_value = mock_company

        use_case = GetCurrentUserUseCase(uow=mock_uow, token_service=mock_token_service)

        request = GetCurrentUserRequest(access_token="fake-access-token")
        with pytest.raises(UserInactiveError) as exc_info:
            await use_case.execute(request)

        assert "La empresa se encuentra suspendida o cancelada." in str(exc_info.value)

    async def test_login_user_raises_inactive_error_when_company_not_active(self, mock_uow: Any, mock_hasher: Any, mock_token_service: Any) -> None:
        user_id = UserId(uuid4())
        company_id = CompanyId(uuid4())

        # Mock user
        mock_user = MagicMock()
        mock_user.id = user_id
        mock_user.empresa_id = company_id
        mock_user.activo = True
        mock_user.password_hash = MagicMock(value="fake-hash")
        mock_uow.users.get_by_email.return_value = mock_user

        # Mock company cancelled
        mock_company = MagicMock()
        mock_company.estado = CompanyStatus.CANCELLED
        mock_uow.companies.get_by_id.return_value = mock_company

        use_case = LoginUserUseCase(uow=mock_uow, hasher=mock_hasher, token_service=mock_token_service)
        request = LoginUserRequest(email="test@example.com", password="Password1!")

        with pytest.raises(UserInactiveError) as exc_info:
            await use_case.execute(request)

        assert "La empresa se encuentra suspendida o cancelada." in str(exc_info.value)

    async def test_refresh_token_raises_inactive_error_when_company_not_active(self, mock_uow: Any, mock_token_service: Any) -> None:
        user_id = UserId(uuid4())
        company_id = CompanyId(uuid4())

        # Mock token service decode
        mock_token_service.decode_token.return_value = {
            "type": "refresh",
            "sub": str(user_id.value),
            "jti": "fake-jti",
            "exp": 123456
        }

        # Mock user
        mock_user = MagicMock()
        mock_user.id = user_id
        mock_user.empresa_id = company_id
        mock_user.activo = True
        mock_uow.users.get_by_id.return_value = mock_user

        # Mock company suspended
        mock_company = MagicMock()
        mock_company.estado = CompanyStatus.SUSPENDED
        mock_uow.companies.get_by_id.return_value = mock_company

        use_case = RefreshTokenUseCase(uow=mock_uow, token_service=mock_token_service)
        request = RefreshTokenRequest(refresh_token="fake-refresh-token")

        with pytest.raises(UserInactiveError) as exc_info:
            await use_case.execute(request)

        assert "La empresa se encuentra suspendida o cancelada." in str(exc_info.value)

    async def test_refresh_token_replay_raises_invalid_token_error(self, mock_uow: Any, mock_token_service: Any) -> None:
        from app.domain.exceptions import InvalidTokenError
        user_id = UserId(uuid4())

        # Mock token service decode
        mock_token_service.decode_token.return_value = {
            "type": "refresh",
            "sub": str(user_id.value),
            "jti": "fake-jti",
            "exp": 123456
        }

        # Mock claim_token to return False (already claimed)
        mock_token_service.claim_token.return_value = False

        use_case = RefreshTokenUseCase(uow=mock_uow, token_service=mock_token_service)
        request = RefreshTokenRequest(refresh_token="fake-refresh-token")

        with pytest.raises(InvalidTokenError) as exc_info:
            await use_case.execute(request)

        assert "Token de refresco ya fue utilizado." in str(exc_info.value)
