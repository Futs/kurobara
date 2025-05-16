import pytest
from tests.utils.test_client import APITestClient

# Admin credentials from settings
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin123"

@pytest.fixture
def admin_client():
    """Fixture to provide an authenticated admin client"""
    client = APITestClient()
    success = client.login(ADMIN_EMAIL, ADMIN_PASSWORD)
    if not success:
        pytest.skip("Could not authenticate as admin")
    yield client
    client.close()

def test_admin_users_access(admin_client):
    """Test admin access to users endpoint"""
    response = admin_client.get("/api/v1/users/")
    assert response.status_code == 200
    users = response.json()
    assert isinstance(users, list)
    print(f"Found {len(users)} users")

def test_manga_endpoints(admin_client):
    """Test manga endpoints"""
    # Test manga listing
    response = admin_client.get("/api/v1/manga/")
    assert response.status_code == 200
    
    # Test manga search
    response = admin_client.get("/api/v1/manga/search", params={"query": "test"})
    assert response.status_code == 200
    
    # Test latest manga
    response = admin_client.get("/api/v1/manga/latest-added")
    assert response.status_code == 200