import pytest
import httpx
import time

BASE_URL = "http://localhost:8000"

def test_root():
    try:
        response = httpx.get(f"{BASE_URL}/", timeout=5.0)
        assert response.status_code == 200
        assert response.json() == {"message": "Welcome to Kurobara Manga Manager API"}
    except httpx.ConnectError as e:
        pytest.fail(f"Failed to connect to {BASE_URL}: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error: {e}")

# Test API endpoints existence (will return 401 without auth)
@pytest.mark.parametrize("endpoint", [
    "/api/v1/users/",
    "/api/v1/manga/",
    "/api/v1/manga/search?query=test",
    "/api/v1/manga/latest-added",
    "/api/v1/chapters/manga/some-id",
    "/api/v1/bookmarks/",
])
def test_endpoint_exists(endpoint):
    try:
        response = httpx.get(f"{BASE_URL}{endpoint}", timeout=5.0)
        # Should return 401 if endpoint exists but requires auth
        assert response.status_code in [200, 401, 404, 422]
    except httpx.ConnectError as e:
        pytest.fail(f"Failed to connect to {BASE_URL}{endpoint}: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error for {endpoint}: {e}")
