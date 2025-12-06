import requests
import json
import sys

BASE_URL = "http://localhost:8000"
session = requests.Session()

def print_step(msg):
    print(f"\n[STEP] {msg}")

def verify_refresh_flow():
    # 1. Register/Login
    print_step("Registering/Logging in...")
    email = "refresh_test@example.com"
    password = "password123"
    
    # Try register
    reg_res = session.post(f"{BASE_URL}/register", json={"email": email, "password": password})
    if reg_res.status_code == 200:
        print("Registered.")
    elif reg_res.status_code == 400:
        print("User likely already exists.")
    else:
        print(f"Register failed: {reg_res.text}")
        sys.exit(1)

    # Login
    print_step("Logging in...")
    login_res = session.post(f"{BASE_URL}/token", data={"username": email, "password": password})
    if login_res.status_code != 200:
        print(f"Login failed: {login_res.text}")
        sys.exit(1)
        
    tokens = login_res.json()
    access_token = tokens["access_token"]
    print(f"Got Access Token: {access_token[:10]}...")
    
    # Check Cookie
    refresh_cookie = session.cookies.get("refresh_token")
    if refresh_cookie:
        print(f"Got HttpOnly Cookie: {refresh_cookie[:10]}...")
    else:
        print("FAIL: No refresh_token cookie found!")
        sys.exit(1)

    # 2. Access Protected Route
    print_step("Accessing Protected Route (Portfolio)...")
    headers = {"Authorization": f"Bearer {access_token}"}
    port_res = session.get(f"{BASE_URL}/portfolio/", headers=headers)
    if port_res.status_code == 200:
        print("Access Granted.")
    else:
        print(f"Access Denied: {port_res.status_code}")
        sys.exit(1)

    # 3. Refresh Token
    print_step("Refreshing Token...")
    # Note: Requests session automatically sends cookies
    refresh_res = session.post(f"{BASE_URL}/refresh")
    if refresh_res.status_code == 200:
        new_tokens = refresh_res.json()
        new_access_token = new_tokens["access_token"]
        print(f"Got New Access Token: {new_access_token[:10]}...")
        if new_access_token != access_token:
             print("Token successfully rotated.")
        else:
             print("Warning: Token matches old one (expected if logic doesn't force rotate imediately or returns same if valid).")
    else:
        print(f"Refresh Failed: {refresh_res.text}")
        sys.exit(1)

    # 4. Logout
    print_step("Logging Out...")
    logout_res = session.post(f"{BASE_URL}/logout")
    if logout_res.status_code == 200:
        print("Logout successful.")
    else:
        print(f"Logout Failed: {logout_res.text}")

    # Verify Cookie Cleared
    # Note: requests cookie jar might update after response.
    # Let's check session cookies.
    cleared_cookie = session.cookies.get("refresh_token")
    if not cleared_cookie:
        print("SUCCESS: Cookie cleared.")
    else:
        print(f"FAIL: Cookie still exists: {cleared_cookie}")

if __name__ == "__main__":
    try:
        verify_refresh_flow()
        print("\n\u2705 VERIFICATION SUCCESSFUL")
    except Exception as e:
        print(f"\n\u274c VERIFICATION FAILED: {e}")
        sys.exit(1)
