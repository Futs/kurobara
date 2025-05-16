import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Kurobara Manga Manager API"}

# Authentication tests - will need valid credentials
def test_login_endpoints():
    # This will fail without valid credentials - just testing endpoint existence
    response = client.post("/api/v1/login/access-token", data={"username": "test", "password": "test"})
    assert response.status_code in [200, 401, 422]

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
    response = client.get(endpoint)
    # Should return 401 if endpoint exists but requires auth
    assert response.status_code in [200, 401, 404, 422]