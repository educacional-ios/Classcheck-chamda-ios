import requests

API_URL = "https://sistema-ios-backend.onrender.com/api"

# Testar com a senha antiga do Jesiel que funcionava antes
print("🔍 Testando senha ANTIGA do Jesiel Junior (antes do reset)\n")

response = requests.post(
    f"{API_URL}/auth/login",
    json={
        "email": "jesiel.junior@ios.org.br",
        "senha": "b99018cd"  # Senha antiga UUID
    },
    timeout=10
)

print(f"Status: {response.status_code}")
print(f"Resposta: {response.text}\n")

print("=" * 80)

# Agora testar com a senha NOVA
print("\n🔍 Testando senha NOVA do Jesiel Junior (depois do reset)\n")

response2 = requests.post(
    f"{API_URL}/auth/login",
    json={
        "email": "jesiel.junior@ios.org.br",
        "senha": "IOS2026jj"  # Senha nova
    },
    timeout=10
)

print(f"Status: {response2.status_code}")
print(f"Resposta: {response2.text}\n")

if response2.status_code == 200:
    print("✅ SENHA NOVA FUNCIONA!")
else:
    print("❌ Senha nova não funciona na API - possível cache do Render")
