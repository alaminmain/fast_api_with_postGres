import requests
import random
import string

BASE_URL = "http://localhost:8000"

def get_random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

email = f"test_{get_random_string(5)}@example.com"
password = "password123"

def test_flow():
    print(f"Testing with User: {email}")
    
    # 1. Register
    print("1. Registering...")
    resp = requests.post(f"{BASE_URL}/register", json={"email": email, "password": password})
    if resp.status_code != 200:
        print(f"Registration failed: {resp.text}")
        return
    print("   Registration Success")

    # 2. Login
    print("2. Logging in...")
    resp = requests.post(f"{BASE_URL}/token", data={"username": email, "password": password})
    if resp.status_code != 200:
        print(f"Login failed: {resp.text}")
        return
    token = resp.json()["access_token"]
    print("   Login Success. Token received.")
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Buy Stock (Assume stock_id 1 exists or fetch one)
    print("3. Fetching stocks to find ID...")
    resp = requests.get(f"{BASE_URL}/market/stocks")
    stocks = resp.json()
    if not stocks:
        print("   No stocks found. Skipping trade.")
        return
    stock_id = stocks[0]["id"]
    print(f"   Using Stock ID: {stock_id} ({stocks[0]['trading_code']})")

    print("4. Buying Stock...")
    buy_data = {
        "stock_id": stock_id,
        "type": "BUY",
        "quantity": 10,
        "price": 100.0
    }
    resp = requests.post(f"{BASE_URL}/portfolio/transactions", json=buy_data, headers=headers)
    if resp.status_code != 200:
        print(f"Buy failed: {resp.text}")
        return
    print("   Buy Success")

    # 5. Check Portfolio
    print("5. Checking Portfolio...")
    resp = requests.get(f"{BASE_URL}/portfolio/", headers=headers)
    if resp.status_code != 200:
         print(f"Portfolio check failed: {resp.text}")
         return
    portfolio = resp.json()
    print(f"   Portfolio found with {len(portfolio)} items.")
    
    # Verify holding
    holding = next((p for p in portfolio if p["stock"]["id"] == stock_id), None)
    if holding and holding["quantity"] == 10:
        print("   Verified: Portfolio updated correctly.")
    else:
        print(f"   Verification Failed: Stock not found or quantity mismatch. Portfolio: {portfolio}")

if __name__ == "__main__":
    test_flow()
