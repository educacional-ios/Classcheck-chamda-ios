import requests
import json

API_URL = "https://sistema-ios-backend.onrender.com/api"

print("🔍 TESTANDO API REAL EM PRODUÇÃO\n")

# Teste 1: Verificar se backend está online
print("1️⃣ Testando se backend está online...")
try:
    response = requests.get(f"{API_URL}/ping", timeout=10)
    print(f"✅ Status: {response.status_code}")
    print(f"   Resposta: {response.json()}\n")
except Exception as e:
    print(f"❌ ERRO: {e}\n")
    exit(1)

# Teste 2: Fazer login
print("2️⃣ Fazendo login com admin...")
login_data = {
    "email": "jesiel.junior@ios.org.br",
    "senha": "b99018cd"
}

try:
    login_response = requests.post(f"{API_URL}/auth/login", json=login_data, timeout=10)
    print(f"   Status: {login_response.status_code}")
    
    if login_response.status_code == 200:
        token = login_response.json().get('access_token')
        print(f"   ✅ Login OK - Token obtido\n")
    else:
        print(f"   ❌ Login falhou: {login_response.text}\n")
        
        # Tentar outros logins possíveis
        print("   Tentando admin@ios.org.br...")
        login_data2 = {"email": "admin@ios.org.br", "senha": "admin123"}
        login_response2 = requests.post(f"{API_URL}/auth/login", json=login_data2, timeout=10)
        if login_response2.status_code == 200:
            token = login_response2.json().get('access_token')
            print(f"   ✅ Login OK com admin@ios.org.br\n")
        else:
            print(f"   ❌ Nenhum login funcionou. Parando aqui.\n")
            exit(1)
            
except Exception as e:
    print(f"   ❌ ERRO: {e}\n")
    exit(1)

# Teste 3: Buscar usuários
print("3️⃣ Buscando lista de usuários...")
headers = {"Authorization": f"Bearer {token}"}

try:
    users_response = requests.get(f"{API_URL}/users", headers=headers, timeout=10)
    print(f"   Status: {users_response.status_code}")
    
    if users_response.status_code == 200:
        usuarios = users_response.json()
        print(f"   ✅ Total de usuários retornados: {len(usuarios)}\n")
        
        print("📋 LISTA DE USUÁRIOS (primeiros 10):\n")
        for i, user in enumerate(usuarios[:10], 1):
            print(f"{i}. {user.get('nome')} - {user.get('email')} ({user.get('tipo')})")
        
        if len(usuarios) > 10:
            print(f"... e mais {len(usuarios) - 10} usuários\n")
        
        # Verificar se as 3 novas estão na lista
        print("\n🔍 VERIFICANDO AS 3 NOVAS USUÁRIAS:\n")
        
        emails_procurados = [
            "fabiana.coelho@ios.org.br",
            "juliete.pereira@ios.org.br",
            "luana.soares@ios.org.br"
        ]
        
        for email in emails_procurados:
            encontrado = next((u for u in usuarios if u.get('email') == email), None)
            if encontrado:
                print(f"✅ ENCONTRADA: {encontrado.get('nome')} ({email})")
            else:
                print(f"❌ NÃO ENCONTRADA: {email}")
        
    else:
        print(f"   ❌ Erro ao buscar usuários: {users_response.text}\n")
        
except Exception as e:
    print(f"   ❌ ERRO: {e}\n")

print("\n" + "="*60)
print("DIAGNÓSTICO COMPLETO")
