from fastapi.testclient import TestClient
import pytest
from src.main import app

client = TestClient(app)

# Test cases for different languages
@pytest.mark.parametrize(
    "language_header, expected_message",
    [
        ({"Accept-Language": "en"}, "Hello World"),
        ({}, "Hello World"), # No header, should default to English
        ({"Accept-Language": "it"}, "Ciao Mondo"),
        ({"Accept-Language": "ru"}, "Привет, мир"),
        ({"Accept-Language": "it-IT,en;q=0.9"}, "Hello World"),
        ({"Accept-Language": "fr"}, "Hello World"), # Unsupported language, should default
    ],
)
def test_root_localization(language_header, expected_message):
    """Test the root endpoint localization with various Accept-Language headers."""
    response = client.get("/", headers=language_header)
    assert response.status_code == 200
    assert response.json() == {"message": expected_message}


def test_invalid_accept_language_header():
    """Test with an invalid Accept-Language header format (should default)."""
    response = client.get("/", headers={"Accept-Language": "invalid-language"})
    assert response.status_code == 200
    # Even with invalid header, fastapi-babel might default gracefully
    # Depending on implementation, it might default to 'en' or handle it differently
    # We'll assume it defaults to 'en' based on our setup
    assert response.json() == {"message": "Hello World"} 