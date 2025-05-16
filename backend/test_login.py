import httpx
import sys
import json

BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin"

def test_login():
    """Test login endpoint with detailed error handling"""
    print(f"Testing login with {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
    
    try:
        # Make the request with detailed debugging
        print("Sending request...")
        response = httpx.post(
            f"{BASE_URL}/api/v1/login/access-token",
            data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            timeout=10.0
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {response.headers}")
        
        # Try to get response body
        try:
            print(f"Response body: {response.text}")
            if response.headers.get("content-type", "").startswith("application/json"):
                print(f"Response JSON: {json.dumps(response.json(), indent=2)}")
        except Exception as e:
            print(f"Error parsing response: {e}")
        
        if response.status_code == 200:
            print("Login successful!")
            return True
        else:
            print(f"Login failed with status code: {response.status_code}")
            return False
            
    except httpx.ConnectError as e:
        print(f"Connection error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_login()
    sys.exit(0 if success else 1)