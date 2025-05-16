import pytest
import httpx
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin@example.com"  # From settings.FIRST_SUPERUSER
ADMIN_PASSWORD = "admin123"  # From settings.FIRST_SUPERUSER_PASSWORD

# Alternative passwords to try if the main one fails
ALT_PASSWORDS = ["admin", "password", "Admin123", "admin@123"]

class TestAdminAuth:
    def setup_method(self):
        """Setup method that runs before each test - get admin token"""
        self.admin_token = self.get_admin_token()
        
    def get_admin_token(self) -> str:
        """Get admin authentication token"""
        # Try with the main password first
        token = self._try_login(ADMIN_EMAIL, ADMIN_PASSWORD)
        if token:
            return token
            
        # If main password fails, try alternatives
        for password in ALT_PASSWORDS:
            print(f"Trying alternative password: {password}")
            token = self._try_login(ADMIN_EMAIL, password)
            if token:
                return token
                
        # If all passwords fail, fail the test
        pytest.fail(f"Failed to authenticate with any password combination")
        return ""
        
    def _try_login(self, email: str, password: str) -> str:
        """Try to login with given credentials"""
        try:
            print(f"Attempting to authenticate with {email}")
            response = httpx.post(
                f"{BASE_URL}/api/v1/login/access-token",
                data={"username": email, "password": password},
                timeout=5.0
            )
            
            print(f"Authentication response status: {response.status_code}")
            
            if response.status_code != 200:
                error_text = response.text
                try:
                    # Try to parse JSON error response for more details
                    error_json = response.json()
                    error_text = f"{error_text} - Detail: {error_json.get('detail', 'No detail')}"
                except:
                    pass
                
                print(f"Login failed: {response.status_code} - {error_text}")
                return ""
            
            token_data = response.json()
            print(f"Admin token obtained: {token_data['access_token'][:10]}...")
            
            # Check if 2FA is required
            if token_data.get("requires_two_factor", False):
                print("Two-factor authentication is required for admin - cannot complete automated test")
                return ""
            
            return token_data["access_token"]
        except Exception as e:
            print(f"Error during login attempt: {str(e)}")
            return ""
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authorization headers with admin token"""
        return {"Authorization": f"Bearer {self.admin_token}"}
    
    def test_admin_access(self):
        """Test admin can access protected endpoints"""
        # Test users endpoint (admin only)
        response = httpx.get(
            f"{BASE_URL}/api/v1/users/",
            headers=self.get_auth_headers(),
            timeout=5.0
        )
        assert response.status_code == 200, f"Failed to access users endpoint: {response.status_code} - {response.text}"
        users = response.json()
        assert isinstance(users, list), "Expected a list of users"
        print(f"Found {len(users)} users in the system")
        
    def test_manga_endpoints(self):
        """Test manga-related endpoints"""
        # Test manga listing
        response = httpx.get(
            f"{BASE_URL}/api/v1/manga/",
            headers=self.get_auth_headers(),
            timeout=5.0
        )
        assert response.status_code == 200, f"Failed to access manga endpoint: {response.status_code} - {response.text}"
        
        # Test manga search
        response = httpx.get(
            f"{BASE_URL}/api/v1/manga/search?query=test",
            headers=self.get_auth_headers(),
            timeout=5.0
        )
        assert response.status_code == 200, f"Failed to access manga search: {response.status_code} - {response.text}"
        
        # Test latest manga
        response = httpx.get(
            f"{BASE_URL}/api/v1/manga/latest-added",
            headers=self.get_auth_headers(),
            timeout=5.0
        )
        assert response.status_code == 200, f"Failed to access latest manga: {response.status_code} - {response.text}"
    
    def test_bookmarks(self):
        """Test bookmarks endpoint"""
        response = httpx.get(
            f"{BASE_URL}/api/v1/bookmarks/",
            headers=self.get_auth_headers(),
            timeout=5.0
        )
        assert response.status_code == 200, f"Failed to access bookmarks: {response.status_code} - {response.text}"
