import httpx
import json

BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin"

def test_admin_auth():
    """Test admin authentication"""
    try:
        print(f"Attempting to authenticate with {ADMIN_EMAIL}")
        response = httpx.post(
            f"{BASE_URL}/api/v1/login/access-token",
            data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            timeout=5.0
        )
        
        print(f"Authentication response status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Failed to authenticate: {response.status_code}")
            print(f"Response: {response.text}")
            try:
                error_json = response.json()
                print(f"Error detail: {error_json.get('detail', 'No detail')}")
            except:
                pass
            return False
            
        token_data = response.json()
        print(f"Authentication successful!")
        print(f"Token: {token_data['access_token'][:10]}...")
        
        # Check if 2FA is required
        if token_data.get("requires_two_factor", False):
            print("Two-factor authentication is required")
            return False
            
        return True
    except Exception as e:
        print(f"Error during authentication: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_admin_auth()
    print(f"Authentication test {'succeeded' if success else 'failed'}")