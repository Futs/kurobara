import httpx
import sys
import time

BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORDS = ["admin123", "admin", "password", "Admin123", "admin@123"]

def check_server_status():
    """Check if the server is running and responding"""
    try:
        response = httpx.get(f"{BASE_URL}/", timeout=5.0)
        print(f"Server status: {response.status_code}")
        print(f"Response: {response.json()}")
        return True
    except httpx.ConnectError:
        print("Failed to connect to server. Is it running?")
        return False
    except Exception as e:
        print(f"Error checking server status: {e}")
        return False

def try_admin_login():
    """Try to login with different admin password combinations"""
    for password in ADMIN_PASSWORDS:
        print(f"\nTrying to login with {ADMIN_EMAIL} / {password}")
        try:
            response = httpx.post(
                f"{BASE_URL}/api/v1/login/access-token",
                data={"username": ADMIN_EMAIL, "password": password},
                timeout=5.0
            )
            
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                token_data = response.json()
                print(f"Login successful with password: {password}")
                print(f"Token: {token_data['access_token'][:10]}...")
                
                # Test a protected endpoint
                headers = {"Authorization": f"Bearer {token_data['access_token']}"}
                users_response = httpx.get(f"{BASE_URL}/api/v1/users/", headers=headers, timeout=5.0)
                print(f"Users endpoint status: {users_response.status_code}")
                
                if users_response.status_code == 200:
                    print("Successfully accessed protected endpoint!")
                    return True
                else:
                    print(f"Failed to access protected endpoint: {users_response.text}")
            else:
                print(f"Login failed: {response.text}")
                try:
                    error_json = response.json()
                    print(f"Error detail: {error_json.get('detail', 'No detail')}")
                except:
                    pass
        except Exception as e:
            print(f"Error during login attempt: {e}")
    
    print("\nAll login attempts failed.")
    return False

def main():
    print("=== Server Diagnostics ===")
    
    # Check if server is running
    print("\nChecking server status...")
    if not check_server_status():
        print("Server check failed. Please make sure the server is running.")
        return False
    
    # Try admin login
    print("\nTrying admin authentication...")
    if not try_admin_login():
        print("Admin authentication failed with all password combinations.")
        return False
    
    print("\nDiagnostics completed successfully!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)