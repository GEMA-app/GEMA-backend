import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from app.application.use_cases.auth.get_current_user import GetCurrentUserUseCase
from app.application.use_cases.auth.login_user import LoginUserUseCase, LoginUserRequest
from app.application.use_cases.auth.refresh_token import RefreshTokenUseCase, RefreshTokenRequest
from app.domain.enums import CompanyStatus
from app.domain.exceptions import UserInactiveError
from app.domain.value_objects import CompanyId, UserId, Email


@pytest.fixture
def mock_uow():
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
def mock_token_service():
    token_service = MagicMock()
    token_service.decode_token = AsyncMock()
    token_service.generate_access_token = AsyncMock()
    token_service.generate_refresh_token = AsyncMock()
    token_service.revoke_token = AsyncMock()
    return token_service


@pytest.fixture
def mock_hasher():
    hasher = MagicMock()
    hasher.verify = MagicMock(return_value=True)
    return hasher


class TestCompanyActiveGuard:

    async def test_get_current_user_raises_inactive_error_when_company_not_active(self, mock_uow, mock_token_service):
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
        
        with pytest.raises(UserInactiveError) as exc_info:
            await use_case.execute("fake-access-token")
            
        assert "La empresa se encuentra suspendida o cancelada." in str(exc_info.value)

    async def test_login_user_raises_inactive_error_when_company_not_active(self, mock_uow, mock_hasher, mock_token_service):
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

    async def test_refresh_token_raises_inactive_error_when_company_not_active(self, mock_uow, mock_token_service):
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
