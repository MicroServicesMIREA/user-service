import pytest
from pydantic import ValidationError

from app.schemas import UserCreate


def test_user_create_valid_data():
    """UserCreate успешно создаётся с валидными полями."""
    user = UserCreate(
        username="test_user",
        email="test@example.com",
        password="secret123",
    )

    assert user.username == "test_user"
    assert user.email == "test@example.com"
    assert user.password == "secret123"


def test_user_create_invalid_email():
    """UserCreate должен валидировать email и кидать ValidationError при некорректном."""
    with pytest.raises(ValidationError):
        UserCreate(
            username="bad_email_user",
            email="not-an-email",  # нет '@' – сработает твой validator в UserBase
            password="secret123",
        )