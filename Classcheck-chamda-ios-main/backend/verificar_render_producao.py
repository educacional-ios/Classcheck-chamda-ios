import asyncio
import httpx

async def verificar_render():
    # URL do backend em produção
    RENDER_URL = "https://sistema-ios-backend.onrender.com"
    
    print("\n" + "="*60)
    print("🔍 VERIFICANDO BACKEND RENDER (PRODUÇÃO)")
    print("="*60 + "\n")
    
    # Fazer login como admin para obter token
    print("🔑 Fazendo login como admin...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Login
            login_data = {
                "email": "admin@ios.com",
                "senha": "Admin@2024"
            }
            
            login_response = await client.post(f"{RENDER_URL}/api/auth/login", json=login_data)
            
            if login_response.status_code != 200:
                print(f"❌ Erro no login: {login_response.status_code}")
                print(f"   Response: {login_response.text}")
                return
            
            token = login_response.json().get("token")
            print(f"✅ Login OK, token obtido\n")
            
            # Buscar stats do dashboard
            headers = {"Authorization": f"Bearer {token}"}
            
            print("📊 Buscando estatísticas do dashboard...")
            stats_response = await client.get(f"{RENDER_URL}/api/dashboard/stats", headers=headers)
            
            if stats_response.status_code == 200:
                stats = stats_response.json()
                print(f"\n✅ ESTATÍSTICAS DO RENDER:")
                print(f"   Total Unidades: {stats.get('total_unidades', 0)}")
                print(f"   Total Cursos: {stats.get('total_cursos', 0)}")
                print(f"   Total Turmas: {stats.get('total_turmas', 0)} ⭐")
                print(f"   Total Alunos: {stats.get('total_alunos', 0)}")
            else:
                print(f"❌ Erro ao buscar stats: {stats_response.status_code}")
            
            # Buscar lista de turmas
            print(f"\n📋 Buscando lista de turmas...")
            turmas_response = await client.get(f"{RENDER_URL}/api/classes", headers=headers)
            
            if turmas_response.status_code == 200:
                turmas = turmas_response.json()
                print(f"\n✅ TURMAS NO RENDER: {len(turmas)} turmas")
                print(f"\nPrimeiras 10:")
                for i, turma in enumerate(turmas[:10], 1):
                    print(f"   {i}. {turma.get('nome', 'SEM NOME')}")
                
                # Verificar se tem Barreiro
                barreiro_turmas = [t for t in turmas if 'barreiro' in t.get('nome', '').lower()]
                if barreiro_turmas:
                    print(f"\n🔍 TURMAS BARREIRO ENCONTRADAS ({len(barreiro_turmas)}):")
                    for t in barreiro_turmas:
                        print(f"   • {t.get('nome')}")
                        print(f"     instrutor_ids: {t.get('instrutor_ids', [])}")
                else:
                    print(f"\n❌ Nenhuma turma Barreiro encontrada")
            else:
                print(f"❌ Erro ao buscar turmas: {turmas_response.status_code}")
                
        except Exception as e:
            print(f"❌ Erro: {e}")
    
    print("\n" + "="*60)
    print("✅ VERIFICAÇÃO CONCLUÍDA")
    print("="*60 + "\n")

if __name__ == "__main__":
    asyncio.run(verificar_render())
