import httpx
from typing import Dict, Any, Optional

class APITestClient:
    """Utility class for testing API endpoints with authentication"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.token = None
        self.client = httpx.Client(timeout=10.0)
    
    def login(self, email: str, password: str) -> bool:
        """Login and get access token"""
        try:
            response = self.client.post(
                f"{self.base_url}/api/v1/login/access-token",
                data={"username": email, "password": password}
            )
            
            if response.status_code != 200:
                print(f"Login failed: {response.status_code} - {response.text}")
                return False
                
            token_data = response.json()
            
            # Check if 2FA is required
            if token_data.get("requires_two_factor", False):
                print("Two-factor authentication is required - cannot complete automated test")
                return False
                
            self.token = token_data["access_token"]
            return True
        except Exception as e:
            print(f"Error during login: {e}")
            return False
    
    def get_headers(self) -> Dict[str, str]:
        """Get headers with authentication token"""
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> httpx.Response:
        """Make GET request with authentication"""
        url = f"{self.base_url}{endpoint}"
        return self.client.get(url, params=params, headers=self.get_headers())
    
    def post(self, endpoint: str, json_data: Optional[Dict[str, Any]] = None, 
             form_data: Optional[Dict[str, Any]] = None) -> httpx.Response:
        """Make POST request with authentication"""
        url = f"{self.base_url}{endpoint}"
        if json_data:
            return self.client.post(url, json=json_data, headers=self.get_headers())
        elif form_data:
            return self.client.post(url, data=form_data, headers=self.get_headers())
        return self.client.post(url, headers=self.get_headers())
    
    def put(self, endpoint: str, json_data: Optional[Dict[str, Any]] = None) -> httpx.Response:
        """Make PUT request with authentication"""
        url = f"{self.base_url}{endpoint}"
        return self.client.put(url, json=json_data, headers=self.get_headers())
    
    def delete(self, endpoint: str) -> httpx.Response:
        """Make DELETE request with authentication"""
        url = f"{self.base_url}{endpoint}"
        return self.client.delete(url, headers=self.get_headers())
    
    def close(self):
        """Close the client session"""
        self.client.close()