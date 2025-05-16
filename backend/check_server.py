import httpx
import sys

def check_server():
    try:
        response = httpx.get("http://localhost:8000/", timeout=5.0)
        print(f"Server is running! Status code: {response.status_code}")
        print(f"Response: {response.json()}")
        return True
    except httpx.ConnectError:
        print("Failed to connect to server at http://localhost:8000")
        print("Make sure the server is running with: uvicorn app.main:app --host 0.0.0.0 --port 8000")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = check_server()
    sys.exit(0 if success else 1)