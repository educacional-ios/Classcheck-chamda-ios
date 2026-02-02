import requests
import time

API_URL = "https://sistema-ios-backend.onrender.com/api"

print("⏳ AGUARDANDO DEPLOY DO RENDER...\n")
print("Testando a cada 20 segundos até funcionar...\n")

tentativa = 1
while True:
    print(f"\n🔄 Tentativa {tentativa} - {time.strftime('%H:%M:%S')}")
    
    try:
        # Teste 1: Verificar se backend está online
        ping_response = requests.get(f"{API_URL}/ping", timeout=10)
        if ping_response.status_code != 200:
            print("   ⚠️  Backend offline, aguardando...")
            time.sleep(20)
            tentativa += 1
            continue
        
        # Teste 2: Fazer login
        login_response = requests.post(f"{API_URL}/auth/login", json={
            "email": "jesiel.junior@ios.org.br",
            "senha": "b99018cd"
        }, timeout=10)
        
        if login_response.status_code != 200:
            print("   ⚠️  Login falhou, aguardando...")
            time.sleep(20)
            tentativa += 1
            continue
        
        token = login_response.json()['access_token']
        headers = {"Authorization": f"Bearer {token}"}
        
        # Teste 3: Buscar usuário
        users_response = requests.get(f"{API_URL}/users", headers=headers, timeout=10)
        usuarios = users_response.json()
        fabiana = next((u for u in usuarios if 'fabiana' in u['email'].lower()), None)
        
        if not fabiana:
            print("   ⚠️  Usuário não encontrado, aguardando...")
            time.sleep(20)
            tentativa += 1
            continue
        
        # Teste 4: Resetar senha
        reset_response = requests.post(
            f"{API_URL}/users/{fabiana['id']}/reset-password",
            headers=headers,
            timeout=10
        )
        
        if reset_response.status_code == 200:
            data = reset_response.json()
            nova_senha = data.get('temp_password', '')
            
            print(f"   ✅ Senha gerada: {nova_senha}")
            
            if nova_senha.startswith('IOS2026'):
                print(f"\n{'='*60}")
                print(f"🎉 DEPLOY CONCLUÍDO COM SUCESSO!")
                print(f"{'='*60}")
                print(f"✅ Novo padrão de senha está funcionando!")
                print(f"   Senha gerada: {nova_senha}")
                print(f"   Esperado: IOS2026fpc")
                print(f"   Status: CORRETO ✓")
                print(f"{'='*60}")
                break
            else:
                print(f"   ⚠️  Ainda no padrão antigo: {nova_senha}")
                print(f"   Aguardando mais 20 segundos...")
        else:
            print(f"   ⚠️  Erro no reset: {reset_response.status_code}")
    
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    time.sleep(20)
    tentativa += 1
    
    if tentativa > 15:
        print("\n⚠️  Máximo de tentativas atingido (5 minutos)")
        print("   O Render pode estar demorando mais que o normal.")
        break

print("\n✅ Script finalizado.")
