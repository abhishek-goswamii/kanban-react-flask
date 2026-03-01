import pytest
from unittest.mock import MagicMock, patch
from app.services.auth_service import AuthService
from app.models.user import User
from app.core.constants import Messages


class TestAuthServiceRegister:
    """tests for auth register logic"""

    def test_register_success(self, mock_db):
        """should register a new user when email is unique"""
        with patch.object(AuthService, "__init__", lambda self, db: None):
            service = AuthService(mock_db)
            service.user_repo = MagicMock()
            service.user_repo.find_by_email.return_value = None

            mock_user = MagicMock(spec=User)
            mock_user.id = 1
            mock_user.email = "test@example.com"
            service.user_repo.create.return_value = mock_user

            user, error = service.register("test@example.com", "Test User", "password123")

            assert user is not None
            assert error is None
            service.user_repo.find_by_email.assert_called_once_with("test@example.com")
            service.user_repo.create.assert_called_once()

    def test_register_duplicate_email(self, mock_db):
        """should return error when email already exists"""
        with patch.object(AuthService, "__init__", lambda self, db: None):
            service = AuthService(mock_db)
            service.user_repo = MagicMock()
            service.user_repo.find_by_email.return_value = MagicMock(spec=User)

            user, error = service.register("existing@example.com", "Test", "pass123")

            assert user is None
            assert error == Messages.EMAIL_ALREADY_EXISTS
            service.user_repo.create.assert_not_called()


class TestAuthServiceLogin:
    """tests for auth login logic"""

    @patch("app.services.auth_service.bcrypt")
    def test_login_success(self, mock_bcrypt, mock_db):
        """should return token on valid credentials"""
        with patch.object(AuthService, "__init__", lambda self, db: None):
            service = AuthService(mock_db)
            service.user_repo = MagicMock()

            mock_user = MagicMock(spec=User)
            mock_user.id = 1
            mock_user.password_hash = "hashed"
            service.user_repo.find_by_email.return_value = mock_user
            mock_bcrypt.checkpw.return_value = True

            token, error = service.login("test@example.com", "password123")

            assert token is not None
            assert error is None

    def test_login_user_not_found(self, mock_db):
        """should return error when user does not exist"""
        with patch.object(AuthService, "__init__", lambda self, db: None):
            service = AuthService(mock_db)
            service.user_repo = MagicMock()
            service.user_repo.find_by_email.return_value = None

            token, error = service.login("missing@example.com", "password123")

            assert token is None
            assert error == Messages.INVALID_CREDENTIALS

    @patch("app.services.auth_service.bcrypt")
    def test_login_wrong_password(self, mock_bcrypt, mock_db):
        """should return error on wrong password"""
        with patch.object(AuthService, "__init__", lambda self, db: None):
            service = AuthService(mock_db)
            service.user_repo = MagicMock()

            mock_user = MagicMock(spec=User)
            mock_user.password_hash = "hashed"
            service.user_repo.find_by_email.return_value = mock_user
            mock_bcrypt.checkpw.return_value = False

            token, error = service.login("test@example.com", "wrong")

            assert token is None
            assert error == Messages.INVALID_CREDENTIALS
