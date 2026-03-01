import pytest
from unittest.mock import MagicMock, patch
from app.models.user import User


@pytest.fixture
def mock_db():
    return MagicMock()
