import asyncio
import httpx

async def migrar_todas_turmas_via_api():
    """Migra TODAS as 56 turmas do Render de instrutor_id para instrutor_ids"""
    RENDER_URL = "https://sistema-ios-backend.onrender.com"
    
    print("\n" + "="*70)
    print("🔄 MIGRANDO TODAS AS TURMAS: instrutor_id → instrutor_ids")
    print("="*70 + "\n")
    
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
        
        # Buscar TODAS as turmas
        print("📋 Buscando todas as turmas...")
        turmas_resp = await client.get(f"{RENDER_URL}/api/classes", headers=headers)
        turmas = turmas_resp.json()
        print(f"   Total: {len(turmas)} turmas\n")
        
        migradas = 0
        erros = 0
        ja_corretas = 0
        
        for i, turma in enumerate(turmas, 1):
            nome = turma['nome']
            turma_id = turma['id']
            
            # Verificar se já tem instrutor_ids (array)
            if 'instrutor_ids' in turma and isinstance(turma['instrutor_ids'], list):
                print(f"{i:2}. ✅ {nome[:60]:<60} [JÁ MIGRADA]")
                ja_corretas += 1
                continue
            
            # Pegar instrutor_id antigo (se existir)
            instrutor_id_antigo = turma.get('instrutor_id')
            
            if not instrutor_id_antigo:
                print(f"{i:2}. ⚠️  {nome[:60]:<60} [SEM INSTRUTOR]")
                continue
            
            # Preparar dados para atualização (converter para array)
            update_data = {
                "nome": turma['nome'],
                "instrutor_ids": [instrutor_id_antigo],  # Converter para array
                "data_inicio": turma.get('data_inicio'),
                "data_fim": turma.get('data_fim'),
                "horario_inicio": turma.get('horario_inicio') or turma.get('hora_inicio'),
                "horario_fim": turma.get('horario_fim') or turma.get('hora_fim'),
                "vagas_total": turma.get('vagas_total') or turma.get('vagas', 25)
            }
            
            # Atualizar via API
            try:
                update_resp = await client.put(
                    f"{RENDER_URL}/api/classes/{turma_id}",
                    json=update_data,
                    headers=headers,
                    timeout=10.0
                )
                
                if update_resp.status_code == 200:
                    print(f"{i:2}. ✅ {nome[:60]:<60} [MIGRADA]")
                    migradas += 1
                else:
                    print(f"{i:2}. ❌ {nome[:60]:<60} [ERRO: {update_resp.status_code}]")
                    erros += 1
                    
            except Exception as e:
                print(f"{i:2}. ❌ {nome[:60]:<60} [EXCEÇÃO: {str(e)[:30]}]")
                erros += 1
        
        print("\n" + "="*70)
        print("📊 RESUMO DA MIGRAÇÃO:")
        print(f"   Total de turmas: {len(turmas)}")
        print(f"   ✅ Migradas agora: {migradas}")
        print(f"   ✅ Já corretas: {ja_corretas}")
        print(f"   ❌ Erros: {erros}")
        print("="*70 + "\n")

if __name__ == "__main__":
    asyncio.run(migrar_todas_turmas_via_api())
