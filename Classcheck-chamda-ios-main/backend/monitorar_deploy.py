import requests
import time
from datetime import datetime

API_URL = "https://sistema-ios-backend.onrender.com/api"

def testar_deploy():
    """Testa se o deploy está completo verificando o timestamp do backend"""
    try:
        response = requests.get(f"{API_URL}/ping", timeout=5)
        if response.status_code == 200:
            data = response.json()
            timestamp = data.get('timestamp', '')
            return True, timestamp
    except:
        pass
    return False, None

def testar_reset_senha():
    """Testa a funcionalidade de reset de senha"""
    print("\n🔐 Testando reset de senha...\n")
    
    # Login
    login_response = requests.post(f"{API_URL}/auth/login", json={
        "email": "jesiel.junior@ios.org.br",
        "senha": "IOS2026jj"
    })
    
    if login_response.status_code != 200:
        print(f"❌ Login falhou: {login_response.status_code}")
        return False
    
    token = login_response.json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    
    # Buscar um usuário para testar
    users_response = requests.get(f"{API_URL}/users", headers=headers)
    if users_response.status_code != 200:
        print(f"❌ Erro ao buscar usuários: {users_response.status_code}")
        return False
    
    usuarios = users_response.json()
    
    # Pegar o ID de algum usuário de teste (ex: Fabiana)
    user_teste = next((u for u in usuarios if 'Fabiana' in u.get('nome', '')), None)
    
    if not user_teste:
        print("⚠️ Usuário de teste não encontrado, usando primeiro da lista")
        user_teste = usuarios[0]
    
    user_id = user_teste['id']
    user_nome = user_teste['nome']
    
    print(f"📝 Testando com: {user_nome}")
    print(f"   ID: {user_id}")
    
    # Reset senha
    reset_response = requests.post(
        f"{API_URL}/users/{user_id}/reset-password",
        headers=headers
    )
    
    if reset_response.status_code == 200:
        nova_senha = reset_response.json().get('senha_temporaria')
        print(f"\n✅ SENHA RESETADA COM SUCESSO!")
        print(f"   Nova senha: {nova_senha}")
        
        # Verificar se está no padrão novo
        if nova_senha and nova_senha.startswith('IOS2026'):
            print(f"   ✅ PADRÃO CORRETO! (IOS2026 + iniciais)")
            return True
        else:
            print(f"   ❌ PADRÃO ANTIGO! (UUID)")
            return False
    else:
        print(f"\n❌ Erro ao resetar senha: {reset_response.status_code}")
        print(f"   Resposta: {reset_response.text}")
        return False

print("🚀 MONITORANDO DEPLOY DO RENDER\n")
print("=" * 70)

ultimo_timestamp = None
tentativa = 0
max_tentativas = 60  # 5 minutos (60 * 5 segundos)

print("⏳ Aguardando deploy...")

while tentativa < max_tentativas:
    tentativa += 1
    tempo_decorrido = tentativa * 5
    
    online, timestamp = testar_deploy()
    
    if online:
        if ultimo_timestamp is None:
            ultimo_timestamp = timestamp
            print(f"✅ Backend online! Timestamp: {timestamp}")
            print(f"   Aguardando atualização...\n")
        elif timestamp != ultimo_timestamp:
            print(f"\n🎉 DEPLOY CONCLUÍDO!")
            print(f"   Timestamp anterior: {ultimo_timestamp}")
            print(f"   Timestamp atual:    {timestamp}")
            print(f"   Tempo decorrido: {tempo_decorrido} segundos\n")
            
            # Aguardar mais 5 segundos para garantir
            print("⏳ Aguardando 5 segundos para estabilizar...")
            time.sleep(5)
            
            # Testar reset de senha
            if testar_reset_senha():
                print("\n" + "=" * 70)
                print("✅ TUDO FUNCIONANDO! Deploy completo e testado.")
                print("=" * 70)
                break
            else:
                print("\n⚠️ Deploy concluído mas função ainda com padrão antigo")
                print("   Pode demorar alguns segundos a mais...")
        else:
            print(f"⏳ [{tempo_decorrido}s] Aguardando... (timestamp: {timestamp[:19]})", end='\r')
    else:
        print(f"⚠️ [{tempo_decorrido}s] Backend offline ou reiniciando...", end='\r')
    
    time.sleep(5)
else:
    print("\n\n⏱️ Timeout - Deploy demorou mais de 5 minutos")
    print("   Tente executar novamente ou verifique manualmente")

print("\n\n📋 PRÓXIMOS PASSOS:")
print("1. Acesse: https://classcheck-chamda-ios.vercel.app")
print("2. Faça login com: jesiel.junior@ios.org.br / IOS2026jj")
print("3. Vá em Usuários")
print("4. Clique em 'Redefinir Senha' em qualquer usuário")
print("5. A senha deve aparecer no formato: IOS2026 + iniciais")
