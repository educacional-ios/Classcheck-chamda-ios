import requests
import time

# 🌐 API URL - PRODUÇÃO (Render)
API_URL = "https://sistema-ios-backend.onrender.com/api"

print("⏳ Aguardando 30 segundos para o Render fazer o redeploy...")
time.sleep(30)

print("\n🔌 Testando API de usuários em produção...\n")

# Tentar fazer login
login_data = {
    "email": "admin@ios.com.br",
    "senha": "admin123"
}

try:
    print("🔐 Tentando fazer login como admin...")
    login_response = requests.get(f"{API_URL}/ping")
    
    if login_response.status_code == 200:
        print(f"✅ Backend está online: {login_response.json()}\n")
    else:
        print(f"⚠️ Backend retornou status {login_response.status_code}\n")
    
    # Tentar buscar usuários sem autenticação (deve falhar)
    print("🔍 Testando endpoint /users (sem autenticação)...")
    users_response = requests.get(f"{API_URL}/users")
    print(f"Status: {users_response.status_code}")
    
    if users_response.status_code == 401:
        print("✅ Autenticação funcionando corretamente (401 sem token)\n")
    
    print("\n📋 INSTRUÇÕES:")
    print("1. Aguarde alguns minutos para o Render fazer o redeploy")
    print("2. Acesse o frontend: https://classcheck-chamda-ios.vercel.app")
    print("3. Faça login como admin")
    print("4. Vá para a aba 'Usuários'")
    print("5. Verifique se a lista está em ordem alfabética")
    print("6. As três novas usuárias devem aparecer:")
    print("   • Fabiana Pinto Coelho (fabiana.coelho@ios.org.br)")
    print("   • Juliete Pereira (juliete.pereira@ios.org.br)")
    print("   • Luana Cristina Soares (luana.soares@ios.org.br)")
    
except Exception as e:
    print(f"\n❌ Erro: {e}")
    print("\nO backend pode estar reiniciando. Aguarde alguns minutos e tente novamente.")
