from src.security.api_key_validator import APIKeyValidator
from datetime import datetime, timedelta
import pytest

def generate_api_key(uuid_part="abcd1234", permissions="standard", days_offset=30):
    future_date = (datetime.now() + timedelta(days=days_offset)).strftime("%Y-%m-%d")
    return f"{uuid_part}-{permissions}-{future_date}"

def test_valid_standard_api_key():
    api_key = generate_api_key(permissions="standard")
    validator = APIKeyValidator(api_key)
    assert validator.validate_api_key() is True
    assert validator.has_permission("standard") is True
    assert validator.has_permission("admin") is False

def test_valid_admin_api_key():
    api_key = generate_api_key(permissions="admin")
    validator = APIKeyValidator(api_key)
    assert validator.validate_api_key() is True
    assert validator.has_permission("admin") is True

def test_valid_multi_permission_key():
    api_key = generate_api_key(permissions="standard,admin")
    validator = APIKeyValidator(api_key)
    assert validator.validate_api_key() is True
    assert validator.has_permission("standard")
    assert validator.has_permission("admin")

def test_invalid_format_api_key():
    invalid_key = "abcd1234standardadmin2025-12-31"
    validator = APIKeyValidator(invalid_key)
    assert validator.validate_api_key() is False

def test_invalid_uuid():
    api_key = generate_api_key(uuid_part="abc123")
    validator = APIKeyValidator(api_key)
    assert validator.validate_api_key() is False

def test_invalid_permissions():
    api_key = generate_api_key(permissions="read,write")
    validator = APIKeyValidator(api_key)
    assert validator.validate_api_key() is False

def test_expired_api_key():
    past_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    expired_key = f"abcd1234-standard,{past_date}"
    validator = APIKeyValidator(expired_key)
    assert validator.validate_api_key() is False