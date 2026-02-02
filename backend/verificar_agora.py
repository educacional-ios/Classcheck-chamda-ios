import asyncio
import httpx

async def verificar_agora():
    RENDER_URL = "https://sistema-ios-backend.onrender.com"
    
    print("\n🔍 Verificando turma Barreiro AGORA no Render...\n")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Login
        login_resp = await client.post(
            f"{RENDER_URL}/api/auth/login",
            json={"email": "jesiel.junior@ios.org.br", "senha": "b99018cd"}
        )
        
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Buscar turmas
        turmas_resp = await client.get(f"{RENDER_URL}/api/classes", headers=headers)
        turmas = turmas_resp.json()
        
        # Encontrar Barreiro Manhã T1
        barreiro = next((t for t in turmas if 'barreiro' in t['nome'].lower() and 'manhã t1' in t['nome'].lower()), None)
        
        if barreiro:
            print(f"✅ {barreiro['nome']}\n")
            
            # Mostrar TODOS os campos relacionados a instrutor
            print("📋 Campos de instrutor:")
            if 'instrutor_id' in barreiro:
                print(f"   instrutor_id (antigo): {barreiro['instrutor_id']}")
            if 'instrutor_ids' in barreiro:
                print(f"   instrutor_ids (novo): {barreiro['instrutor_ids']}")
                
                if barreiro['instrutor_ids']:
                    # Buscar nomes
                    users_resp = await client.get(f"{RENDER_URL}/api/users", headers=headers)
                    users = users_resp.json()
                    
                    print(f"\n👥 Instrutores ({len(barreiro['instrutor_ids'])}):")
                    for inst_id in barreiro['instrutor_ids']:
                        user = next((u for u in users if u['id'] == inst_id), None)
                        if user:
                            print(f"   ✅ {user['nome']}")
                        else:
                            print(f"   ⚠️  ID: {inst_id}")
                else:
                    print(f"\n❌ instrutor_ids está VAZIO")
            
            if 'instrutor_id' not in barreiro and 'instrutor_ids' not in barreiro:
                print(f"   ❌ Nenhum campo de instrutor encontrado!")

if __name__ == "__main__":
    asyncio.run(verificar_agora())
