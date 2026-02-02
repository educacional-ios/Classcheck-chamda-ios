import asyncio
import httpx

async def verificar_turma_barreiro_especifica():
    RENDER_URL = "https://sistema-ios-backend.onrender.com"
    
    print("\n🔍 Verificando turma Barreiro BH Manhã T1...\n")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Login
        login_resp = await client.post(
            f"{RENDER_URL}/api/auth/login",
            json={"email": "jesiel.junior@ios.org.br", "senha": "b99018cd"}
        )
        
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Buscar todas as turmas
        turmas_resp = await client.get(f"{RENDER_URL}/api/classes", headers=headers)
        turmas = turmas_resp.json()
        
        # Encontrar Barreiro Manhã T1
        barreiro_t1 = next((t for t in turmas if 'barreiro' in t['nome'].lower() and 'manhã t1' in t['nome'].lower()), None)
        
        if barreiro_t1:
            print(f"✅ Turma encontrada:")
            print(f"   Nome: {barreiro_t1['nome']}")
            print(f"   ID: {barreiro_t1['id']}")
            print(f"\n📋 CAMPOS COMPLETOS:")
            for key, value in barreiro_t1.items():
                if isinstance(value, list):
                    print(f"   {key}: {value}")
                elif isinstance(value, str) and len(value) > 60:
                    print(f"   {key}: {value[:60]}...")
                else:
                    print(f"   {key}: {value}")
            
            # Verificar se tem instrutor_ids
            if 'instrutor_ids' in barreiro_t1:
                inst_ids = barreiro_t1['instrutor_ids']
                print(f"\n🎯 instrutor_ids: {inst_ids}")
                
                if inst_ids:
                    print(f"\n✅ TEM {len(inst_ids)} INSTRUTOR(ES)!")
                    # Buscar nomes dos instrutores
                    users_resp = await client.get(f"{RENDER_URL}/api/users", headers=headers)
                    users = users_resp.json()
                    
                    for inst_id in inst_ids:
                        instrutor = next((u for u in users if u['id'] == inst_id), None)
                        if instrutor:
                            print(f"   • {instrutor['nome']} ({instrutor['email']})")
                        else:
                            print(f"   • ID: {inst_id} (não encontrado)")
                else:
                    print(f"\n❌ ARRAY VAZIO - SEM INSTRUTORES")
            else:
                print(f"\n❌ Campo 'instrutor_ids' NÃO EXISTE")
        else:
            print("❌ Turma não encontrada")

if __name__ == "__main__":
    asyncio.run(verificar_turma_barreiro_especifica())
