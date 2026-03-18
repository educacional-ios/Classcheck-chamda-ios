import requests
import json

API_URL = "https://sistema-ios-backend.onrender.com/api"
ADMIN_EMAIL = "jesiel.junior@ios.org.br"
ADMIN_PASS = "b99018cd"

def verify():
    # Login
    resp = requests.post(f"{API_URL}/auth/login", json={"email": ADMIN_EMAIL, "senha": ADMIN_PASS})
    if resp.status_code != 200:
        print("Login failed")
        return
        
    token = resp.json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    
    print("✅ Login Success - Verifying Data...")
    
    resp = requests.get(f"{API_URL}/turmas", headers=headers)
    turmas = resp.json()
    
    found_barreiro = False
    found_hortolandia = False
    
    for t in turmas:
        name = t.get('nome')
        instrutors = t.get('instrutor_ids', [])
        
        # Check Barreiro
        if "Barreiro" in name and not found_barreiro:
            print(f"\nExample Barreiro Class: {name}")
            print(f"Instrutor IDs: {instrutors}")
            if len(instrutors) >= 2:
                print("✅ VERIFIED: Has 2 or more instructors")
            else:
                print("❌ FAILED: Found fewer than 2 instructors")
            found_barreiro = True
            
        # Check Hortolandia
        if "Hortolândia" in name and not found_hortolandia:
            print(f"\nExample Hortolandia Class: {name}")
            print(f"Instrutor IDs: {instrutors}")
            if len(instrutors) >= 2:
                print("✅ VERIFIED: Has 2 or more instructors")
            else:
                print("❌ FAILED: Found fewer than 2 instructors")
            found_hortolandia = True
            
        if found_barreiro and found_hortolandia:
            break

if __name__ == "__main__":
    verify()
