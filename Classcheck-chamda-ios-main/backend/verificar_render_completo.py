import asyncio
import httpx
import json

async def verificar_render_completo():
    RENDER_URL = "https://sistema-ios-backend.onrender.com"
    
    print("\n" + "="*60)
    print("🔍 VERIFICANDO RENDER - ANÁLISE COMPLETA")
    print("="*60 + "\n")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            # Login
            print("🔑 Fazendo login...")
            login_response = await client.post(
                f"{RENDER_URL}/api/auth/login",
                json={"email": "jesiel.junior@ios.org.br", "senha": "b99018cd"},
                timeout=30.0
            )
            
            if login_response.status_code != 200:
                print(f"❌ Erro login: {login_response.status_code} - {login_response.text}")
                return
            
            login_data = login_response.json()
            
            if "access_token" in login_data:
                token = login_data["access_token"]
            elif "token" in login_data:
                token = login_data["token"]
            else:
                print(f"❌ Resposta não contém token! Keys: {list(login_data.keys())}")
                return
            
            user = login_data.get("user", {})
            
            print(f"✅ Login OK - {user['nome']} ({user['tipo']})")
            
            # Fazer TODAS as requisições imediatamente com o mesmo token
            headers = {"Authorization": f"Bearer {token}"}
            
            # Requisição 1: Stats
            try:
                print(f"\n📊 Buscando stats...")
                stats_resp = await client.get(f"{RENDER_URL}/api/dashboard/stats", headers=headers, timeout=20.0)
                if stats_resp.status_code == 200:
                    stats = stats_resp.json()
                    print(f"   ✅ Total Turmas (stats): {stats.get('total_turmas', 0)}")
                else:
                    print(f"   ❌ Erro stats: {stats_resp.status_code}")
            except Exception as e:
                print(f"   ❌ Erro: {e}")
            
            # Requisição 2: Lista de turmas (IMEDIATAMENTE após stats)
            try:
                print(f"\n📋 Buscando turmas...")
                turmas_resp = await client.get(f"{RENDER_URL}/api/classes", headers=headers, timeout=20.0)
                
                if turmas_resp.status_code == 200:
                    turmas = turmas_resp.json()
                    print(f"\n✅ TOTAL TURMAS NA API: {len(turmas)}\n")
                    
                    print("="*60)
                    print("LISTA COMPLETA DE TURMAS:")
                    print("="*60)
                    
                    for i, t in enumerate(turmas, 1):
                        nome = t.get('nome', 'SEM NOME')
                        instrutor_ids = t.get('instrutor_ids', [])
                        print(f"{i:2}. {nome}")
                        print(f"    Instrutores ({len(instrutor_ids)}): {instrutor_ids[:2] if len(instrutor_ids) > 0 else '[]'}")
                    
                    # Buscar Barreiro
                    print("\n" + "="*60)
                    print("🔍 TURMAS BARREIRO:")
                    print("="*60)
                    
                    barreiro = [t for t in turmas if 'barreiro' in t.get('nome', '').lower()]
                    
                    if barreiro:
                        print(f"\n✅ {len(barreiro)} turmas encontradas:\n")
                        for t in barreiro:
                            print(f"   • {t['nome']}")
                            print(f"     ID: {t['id']}")
                            print(f"     Instrutores: {t.get('instrutor_ids', [])}\n")
                    else:
                        print("\n❌ Nenhuma turma Barreiro encontrada!\n")
                    
                else:
                    print(f"❌ Erro turmas: {turmas_resp.status_code}")
                    print(f"   Response: {turmas_resp.text[:500]}")
                    
            except Exception as e:
                print(f"❌ Erro: {e}")
                import traceback
                traceback.print_exc()
            
        except Exception as e:
            print(f"❌ Erro geral: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)

if __name__ == "__main__":
    asyncio.run(verificar_render_completo())
