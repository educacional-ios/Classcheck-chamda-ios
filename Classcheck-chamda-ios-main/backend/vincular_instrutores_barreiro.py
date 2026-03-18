import asyncio
import httpx

async def encontrar_e_vincular_instrutores():
    RENDER_URL = "https://sistema-ios-backend.onrender.com"
    
    print("\n" + "="*60)
    print("🔍 BUSCANDO INSTRUTORES E VINCULANDO À TURMA BARREIRO")
    print("="*60 + "\n")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Login
        print("🔑 Fazendo login...")
        login_resp = await client.post(
            f"{RENDER_URL}/api/auth/login",
            json={"email": "jesiel.junior@ios.org.br", "senha": "b99018cd"}
        )
        
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Login OK\n")
        
        # 1. Buscar todos os usuários
        print("👥 Buscando usuários...")
        users_resp = await client.get(f"{RENDER_URL}/api/users", headers=headers)
        users = users_resp.json()
        
        # Encontrar Iago e Raissa
        iago = next((u for u in users if 'iago' in u.get('nome', '').lower()), None)
        raissa = next((u for u in users if 'raissa' in u.get('email', '').lower() or 'raissa' in u.get('nome', '').lower()), None)
        
        # Mostrar todos os instrutores para debug
        print(f"\n   Instrutores disponíveis:")
        instrutores = [u for u in users if u.get('tipo') == 'instrutor']
        for i, inst in enumerate(instrutores[:10], 1):
            print(f"      {i}. {inst.get('nome')} - {inst.get('email')}")
        
        print(f"\n🔍 Instrutores encontrados:")
        if iago:
            print(f"   ✅ Iago: {iago['nome']} - ID: {iago['id']}")
        else:
            print(f"   ❌ Iago não encontrado")
        
        if raissa:
            print(f"   ✅ Raissa: {raissa['nome']} - ID: {raissa['id']}")
        else:
            print(f"   ❌ Raissa não encontrada")
        
        if not (iago and raissa):
            print("\n❌ Não foi possível encontrar ambos os instrutores")
            return
        
        # 2. Buscar turma Barreiro Manhã T1
        print(f"\n📋 Buscando turmas Barreiro...")
        turmas_resp = await client.get(f"{RENDER_URL}/api/classes", headers=headers)
        turmas = turmas_resp.json()
        
        barreiro_turmas = [t for t in turmas if 'barreiro' in t.get('nome', '').lower() and 'manhã t1' in t.get('nome', '').lower()]
        
        if not barreiro_turmas:
            print("❌ Turma 'Barreiro BH Manhã T1' não encontrada")
            return
        
        turma_barreiro = barreiro_turmas[0]
        print(f"\n✅ Turma encontrada:")
        print(f"   Nome: {turma_barreiro['nome']}")
        print(f"   ID: {turma_barreiro['id']}")
        print(f"   Instrutores atuais: {turma_barreiro.get('instrutor_ids', [])}")
        
        # 3. Atualizar turma com os 2 instrutores
        print(f"\n🔧 Vinculando Iago + Raissa à turma...")
        
        # Precisamos enviar apenas os campos que queremos atualizar
        # mas o backend valida campos obrigatórios
        update_data = {
            "nome": turma_barreiro['nome'],
            "instrutor_ids": [iago['id'], raissa['id']],
            "data_inicio": turma_barreiro.get('data_inicio'),
            "data_fim": turma_barreiro.get('data_fim'),
            "horario_inicio": turma_barreiro.get('hora_inicio') or turma_barreiro.get('horario_inicio'),
            "horario_fim": turma_barreiro.get('hora_fim') or turma_barreiro.get('horario_fim'),
            "vagas_total": turma_barreiro.get('vagas') or turma_barreiro.get('vagas_total', 25)
        }
        
        update_resp = await client.put(
            f"{RENDER_URL}/api/classes/{turma_barreiro['id']}",
            json=update_data,
            headers=headers
        )
        
        if update_resp.status_code == 200:
            turma_atualizada = update_resp.json()
            print(f"\n✅ TURMA ATUALIZADA COM SUCESSO!")
            print(f"   Nome: {turma_atualizada['nome']}")
            print(f"   Instrutores: {turma_atualizada.get('instrutor_ids', [])}")
            print(f"   Total: {len(turma_atualizada.get('instrutor_ids', []))} instrutores")
            
            print(f"\n🎯 Agora Raissa e Iago verão a turma Barreiro!")
        else:
            print(f"\n❌ Erro ao atualizar: {update_resp.status_code}")
            print(f"   Response: {update_resp.text}")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    asyncio.run(encontrar_e_vincular_instrutores())
