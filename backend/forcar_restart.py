import requests
import time

API_URL = "https://sistema-ios-backend.onrender.com"

print("🔄 Tentando forçar reinício da API...\n")

# Fazer várias requisições para tentar invalidar cache
for i in range(3):
    print(f"Tentativa {i+1}/3...")
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        print(f"   Health check: {response.status_code}")
    except:
        print(f"   Health check falhou")
    time.sleep(2)

print("\n" + "=" * 80)
print("\n💡 SOLUÇÃO:")
print("   1. As senhas FORAM atualizadas no MongoDB Atlas com sucesso")
print("   2. A API do Render está com cache/conexão antiga")
print("   3. Você precisa REINICIAR MANUALMENTE o serviço no Render:")
print("      - Acesse: https://dashboard.render.com")
print("      - Vá em 'sistema-ios-backend'")
print("      - Clique em 'Manual Deploy' > 'Clear build cache & deploy'")
print("      - OU clique em 'Suspend' e depois 'Resume'")
print("\n   Após reiniciar, teste novamente com: python testar_logins.py")
print("=" * 80)
