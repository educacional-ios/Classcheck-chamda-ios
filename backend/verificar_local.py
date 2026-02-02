import asyncio
import httpx

async def verificar_turma_local():
    """Verifica turma Barreiro no servidor LOCAL (porta 8001)"""
    LOCAL_URL = "http://localhost:8001"
    
    print("\n🔍 Verificando turma Barreiro no servidor LOCAL...\n")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            # Login
            login_resp = await client.post(
                f"{LOCAL_URL}/api/auth/login",
                json={"email": "jesiel.junior@ios.org.br", "senha": "b99018cd"}
            )
            
            if login_resp.status_code != 200:
                print(f"❌ Erro login: {login_resp.text}")
                return
            
            token = login_resp.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # Buscar turmas
            turmas_resp = await client.get(f"{LOCAL_URL}/api/classes", headers=headers)
            turmas = turmas_resp.json()
            
            # Encontrar Barreiro Manhã T1
            barreiro = next((t for t in turmas if 'barreiro' in t['nome'].lower() and 'manhã t1' in t['nome'].lower()), None)
            
            if barreiro:
                print(f"✅ Turma encontrada: {barreiro['nome']}\n")
                
                # Verificar instrutor_ids
                if 'instrutor_ids' in barreiro:
                    inst_ids = barreiro['instrutor_ids']
                    print(f"📋 instrutor_ids: {inst_ids}")
                    print(f"   Total: {len(inst_ids)} instrutor(es)\n")
                    
                    if inst_ids:
                        # Buscar nomes
                        users_resp = await client.get(f"{LOCAL_URL}/api/users", headers=headers)
                        users = users_resp.json()
                        
                        print("👥 Instrutores vinculados:")
                        for inst_id in inst_ids:
                            user = next((u for u in users if u['id'] == inst_id), None)
                            if user:
                                print(f"   ✅ {user['nome']} ({user['email']})")
                            else:
                                print(f"   ⚠️  ID {inst_id} (usuário não encontrado)")
                    else:
                        print("❌ Array vazio - SEM INSTRUTORES")
                else:
                    print("❌ Campo instrutor_ids NÃO EXISTE")
                    print(f"\nCampos disponíveis: {list(barreiro.keys())}")
            else:
                print("❌ Turma Barreiro não encontrada")
                
        except Exception as e:
            print(f"❌ Erro: {e}")

if __name__ == "__main__":
    asyncio.run(verificar_turma_local())
