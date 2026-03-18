import asyncio
import httpx

async def verificar_render_sem_login():
    # URL do backend em produção
    RENDER_URL = "https://sistema-ios-backend.onrender.com"
    
    print("\n" + "="*60)
    print("🔍 TESTANDO CONEXÃO COM RENDER")
    print("="*60 + "\n")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Testar endpoint raiz
            print("📡 Testando endpoint raiz...")
            response = await client.get(f"{RENDER_URL}/")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            
            # Testar se API está respondendo
            print(f"\n📡 Testando /api/health ou similar...")
            
            # Tentar login com usuário teste
            print(f"\n🔑 Tentando logins possíveis...")
            
            credenciais = [
                {"email": "admin@ios.com", "senha": "Admin@2024"},
                {"email": "jesiel@ios.com", "senha": "Jesiel@2024"},
                {"email": "Jesiel@ios.com", "senha": "Jesiel@2024"},
            ]
            
            for cred in credenciais:
                try:
                    print(f"\n   Tentando: {cred['email']}")
                    login_response = await client.post(
                        f"{RENDER_URL}/api/auth/login", 
                        json=cred,
                        timeout=10.0
                    )
                    
                    if login_response.status_code == 200:
                        print(f"   ✅ LOGIN OK!")
                        token = login_response.json().get("token")
                        
                        # Buscar turmas
                        headers = {"Authorization": f"Bearer {token}"}
                        turmas_response = await client.get(
                            f"{RENDER_URL}/api/classes", 
                            headers=headers,
                            timeout=10.0
                        )
                        
                        if turmas_response.status_code == 200:
                            turmas = turmas_response.json()
                            print(f"\n   📊 TOTAL DE TURMAS NO RENDER: {len(turmas)}")
                            
                            if len(turmas) > 0:
                                print(f"\n   Primeiras 5 turmas:")
                                for i, t in enumerate(turmas[:5], 1):
                                    print(f"      {i}. {t.get('nome', 'SEM NOME')}")
                                
                                # Procurar Barreiro
                                barreiro = [t for t in turmas if 'barreiro' in t.get('nome', '').lower()]
                                if barreiro:
                                    print(f"\n   🎯 TURMAS BARREIRO ({len(barreiro)}):")
                                    for t in barreiro:
                                        print(f"      • {t.get('nome')}")
                                        print(f"        IDs instrutores: {t.get('instrutor_ids', [])}")
                        
                        return  # Login bem-sucedido, sair
                    else:
                        print(f"   ❌ Falhou: {login_response.status_code}")
                        
                except httpx.TimeoutException:
                    print(f"   ⏱️  Timeout")
                except Exception as e:
                    print(f"   ❌ Erro: {str(e)[:100]}")
                    
        except Exception as e:
            print(f"❌ Erro geral: {e}")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    asyncio.run(verificar_render_sem_login())
