import requests
import time

API_URL = "https://sistema-ios-backend.onrender.com/api"
RAISSA_EMAIL = "raissa.pinho@ios.org.br"
RAISSA_PASS = "2b7b2e77"

def check():
    print("Testing Debug Endpoint...")
    
    # Login
    try:
        resp = requests.post(f"{API_URL}/auth/login", json={"email": RAISSA_EMAIL, "senha": RAISSA_PASS})
        if resp.status_code != 200:
            print(f"Login Failed: {resp.status_code}")
            return
        token = resp.json()['access_token']
        headers = {"Authorization": f"Bearer {token}"}
    except Exception as e:
        print(f"Connection Error: {e}")
        return

    # Hit Debug
    url = f"{API_URL}/debug/visibility"
    print(f"GET {url}")
    
    try:
        resp = requests.get(url, headers=headers)
        if resp.status_code == 404:
            print("Endpoint NOT FOUND (Old version running)")
        elif resp.status_code == 200:
            print("Sucess! Response:")
            print(resp.json())
        else:
            print(f"Error: {resp.status_code}")
            print(resp.text)
    except Exception as e:
        print(f"Debug Request Error: {e}")

if __name__ == "__main__":
    check()
