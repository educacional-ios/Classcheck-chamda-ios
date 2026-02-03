import requests
import json
import sys

# Config
API_URL = "https://sistema-ios-backend.onrender.com/api"
RAISSA_EMAIL = "raissa.pinho@ios.org.br"
# Using the password seen in the other file
RAISSA_PASS = "2b7b2e77" 

def testar():
    print("=" * 60)
    print("TESTE DE VERIFICAÇÃO PÓS-DEPLOY")
    print("=" * 60)
    
    # 1. Login
    print(f"\n🔐 Logando como {RAISSA_EMAIL}...")
    try:
        resp = requests.post(f"{API_URL}/auth/login", json={"email": RAISSA_EMAIL, "senha": RAISSA_PASS})
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return

    if resp.status_code != 200:
        print(f"❌ Falha no login: {resp.status_code}")
        print(resp.text)
        return

    data = resp.json()
    token = data['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login sucesso!")

    # 2. Get Classes
    print("\n📚 Buscando turmas...")
    resp_classes = requests.get(f"{API_URL}/classes", headers=headers)
    
    if resp_classes.status_code != 200:
        print(f"❌ Erro ao buscar turmas: {resp_classes.status_code}")
        print(resp_classes.text)
        return
        
    turmas = resp_classes.json()
    print(f"🔢 Total de turmas retornadas: {len(turmas)}")
    
    # 3. Analyze
    found_demo = False
    for t in turmas:
        nome = t.get('nome', 'Sem Nome')
        instrutor_ids = t.get('instrutor_ids', [])
        old_id = t.get('instrutor_id')
        
        print(f" - {nome} | IDs: {instrutor_ids} | OldID: {old_id}")
        
        if "DEMO 2 INSTRUTORES" in nome:
            found_demo = True
            print("   🌟 TURMA DEMO ENCONTRADA! SUCESSO!")
            
    if not found_demo:
        print("\n❌ ERRO: Turma DEMO não foi encontrada na lista da Raissa.")
    else:
        print("\n✅ SUCESSO: Turma DEMO visível para Raissa.")

if __name__ == "__main__":
    testar()
