import asyncio
import httpx

async def verificar_render_com_credenciais():
    RENDER_URL = "https://sistema-ios-backend.onrender.com"
    
    print("\n" + "="*60)
    print("🔍 VERIFICANDO RENDER COM CREDENCIAIS CORRETAS")
    print("="*60 + "\n")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Login com credenciais corretas
            print("🔑 Fazendo login como admin...")
            login_data = {
                "email": "jesiel.junior@ios.org.br",
                "senha": "b99018cd"
            }
            
            login_response = await client.post(f"{RENDER_URL}/api/auth/login", json=login_data)
            
            if login_response.status_code != 200:
                print(f"❌ Erro no login: {login_response.status_code}")
                print(f"   Response: {login_response.text}")
                return
            
            login_json = login_response.json()
            token = login_json.get("token")
            print(f"✅ Login OK!")
            print(f"   User: {login_json.get('user', {}).get('nome')}")
            print(f"   Tipo: {login_json.get('user', {}).get('tipo')}\n")
            
            headers = {"Authorization": f"Bearer {token}"}
            
            # 1. Buscar stats
            print("📊 Buscando estatísticas...")
            stats_response = await client.get(f"{RENDER_URL}/api/dashboard/stats", headers=headers, timeout=15.0)
            
            if stats_response.status_code == 200:
                stats = stats_response.json()
                print(f"✅ STATS DO DASHBOARD:")
                print(f"   Unidades: {stats.get('total_unidades', 0)}")
                print(f"   Cursos: {stats.get('total_cursos', 0)}")
                print(f"   ⭐ TURMAS: {stats.get('total_turmas', 0)} ⭐")
                print(f"   Alunos: {stats.get('total_alunos', 0)}\n")
            
            # 2. Buscar TODAS as turmas
            print("📋 Buscando lista completa de turmas...")
            turmas_response = await client.get(f"{RENDER_URL}/api/classes", headers=headers, timeout=15.0)
            
            if turmas_response.status_code == 200:
                turmas = turmas_response.json()
                print(f"\n✅ TOTAL DE TURMAS NO RENDER: {len(turmas)}\n")
                
                print("="*60)
                print("TODAS AS TURMAS:")
                print("="*60)
                for i, turma in enumerate(turmas, 1):
                    instrutor_ids = turma.get('instrutor_ids', [])
                    print(f"{i}. {turma.get('nome', 'SEM NOME')}")
                    print(f"   ID: {turma.get('id')}")
                    print(f"   Instrutores: {len(instrutor_ids)} - {instrutor_ids}")
                
                # Procurar Barreiro especificamente
                print("\n" + "="*60)
                print("🔍 PROCURANDO TURMAS BARREIRO:")
                print("="*60)
                barreiro_turmas = [t for t in turmas if 'barreiro' in t.get('nome', '').lower()]
                
                if barreiro_turmas:
                    print(f"\n✅ Encontradas {len(barreiro_turmas)} turmas Barreiro:\n")
                    for t in barreiro_turmas:
                        print(f"   • {t.get('nome')}")
                        print(f"     ID: {t.get('id')}")
                        print(f"     instrutor_ids: {t.get('instrutor_ids', [])}")
                        print()
                else:
                    print("\n❌ NENHUMA turma Barreiro encontrada!")
                
            else:
                print(f"❌ Erro ao buscar turmas: {turmas_response.status_code}")
                print(f"   Response: {turmas_response.text}")
                
        except Exception as e:
            print(f"❌ Erro: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print("✅ VERIFICAÇÃO CONCLUÍDA")
    print("="*60 + "\n")

if __name__ == "__main__":
    asyncio.run(verificar_render_com_credenciais())
