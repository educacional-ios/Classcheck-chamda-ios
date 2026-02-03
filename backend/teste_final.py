import requests

API_URL = "https://sistema-ios-backend.onrender.com"

print("\n" + "="*80)
print("🎯 TESTE FINAL - VERIFICANDO BANCO CORRETO")
print("="*80)

# Login admin
print("\n1️⃣ Fazendo login...")
login = requests.post(
    f"{API_URL}/api/auth/login",
    json={"email": "jesiel.junior@ios.org.br", "senha": "b99018cd"}
)

if login.status_code != 200:
    print(f"❌ Erro no login: {login.status_code}")
    exit(1)

print("✅ Login OK!")
token = login.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Buscar turmas
print("\n2️⃣ Buscando turmas...")
turmas = requests.get(f"{API_URL}/api/classes", headers=headers).json()

print(f"Total: {len(turmas)} turmas")

# Procurar DEMO
demo = None
for t in turmas:
    if "DEMO" in t.get('nome', '').upper():
        demo = t
        break

if demo:
    print(f"\n🎉 SUCESSO! TURMA DEMO ENCONTRADA!")
    print(f"   Nome: {demo.get('nome')}")
    print(f"   instrutor_ids: {demo.get('instrutor_ids')}")
    
    if len(turmas) == 21 and demo.get('instrutor_ids') and len(demo.get('instrutor_ids')) == 2:
        print(f"\n✅ TUDO CERTO!")
        print(f"   - 21 turmas ✅")
        print(f"   - Turma DEMO com 2 instrutores ✅")
        print(f"\n🎯 Agora teste no sistema:")
        print(f"   Login Raissa: raissa.pinho@ios.org.br / b99018cd")
        print(f"   Login Iago: iago.herbert@ios.org.br / b99018cd")
        print(f"   Ambos devem ver a turma DEMO!")
    else:
        print(f"\n⚠️  Turmas: {len(turmas)} (esperado 21)")
else:
    print(f"\n❌ Turma DEMO não encontrada")
    print(f"   Total de turmas: {len(turmas)}")
    if len(turmas) == 57:
        print(f"   ⚠️  AINDA no banco antigo!")
    elif len(turmas) == 21:
        print(f"   ✅ Banco correto, mas falta criar a turma DEMO")

print("\n" + "="*80)
