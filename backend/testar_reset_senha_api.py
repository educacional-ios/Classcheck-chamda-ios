import requests
import time

API_URL = "https://sistema-ios-backend.onrender.com/api"

print("🔍 TESTANDO NOVA GERAÇÃO DE SENHA...\n")

# Login - testar com senha antiga primeiro
login_response = requests.post(f"{API_URL}/auth/login", json={
    "email": "jesiel.junior@ios.org.br",
    "senha": "b99018cd"
})

if login_response.status_code != 200:
    print(f"❌ Login falhou. Verifique se a senha foi atualizada.")
    exit(1)

token = login_response.json()['access_token']
headers = {"Authorization": f"Bearer {token}"}

print("✅ Login OK\n")

# Buscar um usuário de teste (Fabiana)
users_response = requests.get(f"{API_URL}/users", headers=headers)
usuarios = users_response.json()

# Procurar Fabiana Pinto Coelho
fabiana = next((u for u in usuarios if 'fabiana' in u['email'].lower()), None)

if not fabiana:
    print("❌ Usuário de teste não encontrado")
    exit(1)

print(f"👤 Testando com: {fabiana['nome']}")
print(f"📧 Email: {fabiana['email']}")
print(f"🆔 ID: {fabiana['id']}\n")

print("🔐 Resetando senha via API...")

# Resetar senha
reset_response = requests.post(
    f"{API_URL}/users/{fabiana['id']}/reset-password",
    headers=headers
)

if reset_response.status_code == 200:
    data = reset_response.json()
    nova_senha = data.get('temp_password', data.get('senha_temporaria', 'NÃO ENCONTRADA'))
    
    print(f"\n✅ SENHA RESETADA COM SUCESSO!")
    print(f"📋 Nova senha: {nova_senha}")
    print(f"📦 Resposta completa: {data}")
    
    if nova_senha.startswith('IOS2026'):
        print(f"\n🎉 PADRÃO NOVO FUNCIONANDO!")
        print(f"   Esperado: IOS2026fpc")
        print(f"   Recebido: {nova_senha}")
    else:
        print(f"\n⚠️  AINDA ESTÁ NO PADRÃO ANTIGO")
        print(f"   A senha deveria começar com IOS2026")
        print(f"   Mas gerou: {nova_senha}")
else:
    print(f"❌ Erro ao resetar: {reset_response.status_code}")
    print(f"   {reset_response.text}")
