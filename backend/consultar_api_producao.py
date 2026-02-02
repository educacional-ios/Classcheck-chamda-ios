import requests
import json

# URL da API em produção no Render
API_URL = "https://sistema-ios-backend.onrender.com/api"

print("🌐 Consultando API de Produção no Render...")
print(f"URL: {API_URL}\n")

try:
    # Fazer login admin primeiro
    print("🔐 Fazendo login...")
    login_data = {
        "email": "admin@ios.com.br",
        "senha": "IOS2026a"
    }
    login_response = requests.post(f"{API_URL}/auth/login", json=login_data, timeout=30)
    
    print(f"Login Status: {login_response.status_code}")
    
    if login_response.status_code != 200:
        print(f"❌ Falha no login: {login_response.text}")
        exit(1)
    
    token = login_response.json().get('access_token')
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login bem-sucedido!\n")
    
    # Agora buscar usuários com token
    response = requests.get(f"{API_URL}/users", headers=headers, timeout=30)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        usuarios = response.json()
        print(f"\n✅ Total de usuários encontrados: {len(usuarios)}\n")
        print("=" * 140)
        print(f"{'#':<4} {'Nome':<40} {'Email':<45} {'Tipo':<25}")
        print("=" * 140)
        
        for i, user in enumerate(usuarios, 1):
            nome = user.get('nome', 'N/A')
            email = user.get('email', 'N/A')
            tipo = user.get('tipo', 'N/A')
            
            # Gerar senha no padrão
            palavras = nome.strip().split()
            iniciais = ''.join([p[0].lower() for p in palavras if p])[:5]
            senha = f"IOS2026{iniciais}"
            
            print(f"{i:<4} {nome:<40} {email:<45} {tipo:<25}")
        
        print("=" * 140)
        
        # Buscar especificamente Dayane e Amanda
        print("\n🔍 Procurando Dayane e Amanda...")
        dayane = [u for u in usuarios if 'dayane' in u.get('nome', '').lower() or 'dayane' in u.get('email', '').lower()]
        amanda = [u for u in usuarios if 'amanda' in u.get('nome', '').lower() or 'amanda' in u.get('email', '').lower()]
        
        if dayane:
            print("\n✅ DAYANE ENCONTRADA:")
            for u in dayane:
                nome = u.get('nome')
                palavras = nome.strip().split()
                iniciais = ''.join([p[0].lower() for p in palavras if p])[:5]
                senha = f"IOS2026{iniciais}"
                print(f"   Nome: {u.get('nome')}")
                print(f"   Email: {u.get('email')}")
                print(f"   Tipo: {u.get('tipo')}")
                print(f"   Senha: {senha}")
        
        if amanda:
            print("\n✅ AMANDA ENCONTRADA:")
            for u in amanda:
                nome = u.get('nome')
                palavras = nome.strip().split()
                iniciais = ''.join([p[0].lower() for p in palavras if p])[:5]
                senha = f"IOS2026{iniciais}"
                print(f"   Nome: {u.get('nome')}")
                print(f"   Email: {u.get('email')}")
                print(f"   Tipo: {u.get('tipo')}")
                print(f"   Senha: {senha}")
        
    elif response.status_code == 401:
        print("❌ Endpoint requer autenticação")
        print("Tentando com login admin...")
        
        # Fazer login
        login_data = {
            "email": "admin@ios.com.br",
            "senha": "IOS2026a"
        }
        login_response = requests.post(f"{API_URL}/login", json=login_data, timeout=30)
        
        if login_response.status_code == 200:
            token = login_response.json().get('access_token')
            headers = {"Authorization": f"Bearer {token}"}
            
            # Buscar usuários com token
            response = requests.get(f"{API_URL}/users", headers=headers, timeout=30)
            usuarios = response.json()
            
            print(f"\n✅ Total de usuários: {len(usuarios)}\n")
            
            for user in usuarios:
                print(f"{user.get('nome')} - {user.get('email')} - {user.get('tipo')}")
    else:
        print(f"❌ Erro: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"❌ Erro ao consultar API: {e}")
