import requests
import json

API_URL = "https://sistema-ios-backend.onrender.com"
RAISSA_ID = "41082b8d-4359-4fdd-a5e2-98c54871bf31"
IAGO_ID = "03dea76b-9932-4240-982b-bf406bb3f003"

print("\n" + "="*80)
print("🔍 TESTANDO API DO RENDER - LOGIN RAISSA")
print("="*80)

# 1. Login Raissa
print("\n1️⃣ Fazendo login como Raissa...")
login_response = requests.post(
    f"{API_URL}/login",
    json={
        "email": "raissa.pinho@ios.org.br",
        "senha": "b99018cd"
    }
)

if login_response.status_code == 200:
    print("✅ Login OK!")
    raissa_data = login_response.json()
    print(f"   ID: {raissa_data.get('id')}")
    print(f"   Nome: {raissa_data.get('nome')}")
    print(f"   Cargo: {raissa_data.get('cargo')}")
else:
    print(f"❌ Erro no login: {login_response.status_code}")
    print(login_response.text)
    exit(1)

# 2. Buscar turmas do Raissa
print("\n2️⃣ Buscando turmas de Raissa via API...")
turmas_response = requests.get(f"{API_URL}/classes?instrutor_id={RAISSA_ID}")

print(f"   Status: {turmas_response.status_code}")
if turmas_response.status_code == 200:
    turmas = turmas_response.json()
    print(f"   Turmas retornadas: {len(turmas)}")
    
    if turmas:
        for t in turmas:
            print(f"\n   📚 {t.get('nome')}")
            print(f"      ID: {t.get('id')}")
            print(f"      instrutor_id: {t.get('instrutor_id')}")
            print(f"      instrutor_ids: {t.get('instrutor_ids')}")
    else:
        print("   ❌ NENHUMA TURMA RETORNADA!")
else:
    print(f"   ❌ Erro: {turmas_response.status_code}")
    print(turmas_response.text)

# 3. Buscar turma DEMO diretamente
print("\n3️⃣ Buscando turma DEMO diretamente...")
demo_response = requests.get(f"{API_URL}/classes")

if demo_response.status_code == 200:
    todas_turmas = demo_response.json()
    print(f"   Total de turmas na API: {len(todas_turmas)}")
    
    # Procurar a DEMO
    demo = None
    for t in todas_turmas:
        if "DEMO" in t.get('nome', ''):
            demo = t
            break
    
    if demo:
        print(f"\n   ✅ TURMA DEMO ENCONTRADA NA API:")
        print(f"      Nome: {demo.get('nome')}")
        print(f"      ID: {demo.get('id')}")
        print(f"      instrutor_id: {demo.get('instrutor_id')}")
        print(f"      instrutor_ids: {demo.get('instrutor_ids')}")
    else:
        print("   ❌ TURMA DEMO NÃO ENCONTRADA NA API!")
        print("   Backend não está retornando a turma que está no MongoDB!")
else:
    print(f"   ❌ Erro: {demo_response.status_code}")

# 4. Testar endpoint com instrutor_ids
print("\n4️⃣ Testando filtro por instrutor_ids...")
turmas_ids_response = requests.get(f"{API_URL}/classes?instrutor_ids={RAISSA_ID}")
print(f"   Status: {turmas_ids_response.status_code}")

if turmas_ids_response.status_code == 200:
    turmas_ids = turmas_ids_response.json()
    print(f"   Turmas retornadas: {len(turmas_ids)}")
    if turmas_ids:
        for t in turmas_ids:
            print(f"      - {t.get('nome')}")
else:
    print(f"   Erro ou parâmetro não suportado")

print("\n" + "="*80)
