import requests

API_URL = "https://sistema-ios-backend.onrender.com/api"

# Lista de usuários para testar
usuarios_teste = [
    {"nome": "Administrador", "email": "admin@ios.com.br", "senha": "IOS2026a"},
    {"nome": "Jesiel Junior", "email": "jesiel.junior@ios.org.br", "senha": "IOS2026jj"},
    {"nome": "Fabiana Pinto Coelho", "email": "fabiana.coelho@ios.org.br", "senha": "IOS2026fpc"},
    {"nome": "Juliete Pereira", "email": "juliete.pereira@ios.org.br", "senha": "IOS2026jp"},
    {"nome": "Luana Cristina Soares", "email": "luana.soares@ios.org.br", "senha": "IOS2026lcs"},
    {"nome": "Iago Herbert dos Santos", "email": "iago.santos@ios.org.br", "senha": "IOS2026ihds"},
]

print("🔐 TESTANDO LOGIN COM SENHAS ATUALIZADAS\n")
print("=" * 80)

sucessos = 0
falhas = 0

for user in usuarios_teste:
    print(f"\n👤 {user['nome']}")
    print(f"   Email: {user['email']}")
    print(f"   Senha: {user['senha']}")
    
    try:
        response = requests.post(
            f"{API_URL}/auth/login",
            json={"email": user['email'], "senha": user['senha']},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token', '')[:30]
            print(f"   ✅ LOGIN SUCESSO! Token: {token}...")
            sucessos += 1
        else:
            print(f"   ❌ LOGIN FALHOU: {response.status_code}")
            print(f"      Resposta: {response.text}")
            falhas += 1
            
    except Exception as e:
        print(f"   ❌ ERRO: {e}")
        falhas += 1

print("\n" + "=" * 80)
print(f"\n📊 RESULTADO:")
print(f"   ✅ Sucessos: {sucessos}/{len(usuarios_teste)}")
print(f"   ❌ Falhas: {falhas}/{len(usuarios_teste)}")

if sucessos == len(usuarios_teste):
    print(f"\n🎉 TODAS AS SENHAS ESTÃO FUNCIONANDO PERFEITAMENTE!")
elif sucessos > 0:
    print(f"\n⚠️  Algumas senhas funcionaram, mas nem todas.")
else:
    print(f"\n❌ NENHUMA SENHA FUNCIONOU - Verificar problema no sistema")

print("=" * 80)
