import asyncio
import httpx

async def descobrir_configuracao_render():
    """Consulta API do Render para descobrir qual banco ele está usando"""
    RENDER_URL = "https://sistema-ios-backend.onrender.com"
    
    print("\n" + "="*70)
    print("🔍 DESCOBRINDO CONFIGURAÇÃO REAL DO RENDER")
    print("="*70 + "\n")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Login
        login_resp = await client.post(
            f"{RENDER_URL}/api/auth/login",
            json={"email": "jesiel.junior@ios.org.br", "senha": "b99018cd"}
        )
        
        if login_resp.status_code != 200:
            print(f"❌ Erro login: {login_resp.text}")
            return
        
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Buscar turmas
        turmas_resp = await client.get(f"{RENDER_URL}/api/classes", headers=headers)
        turmas = turmas_resp.json()
        
        print(f"📊 RENDER EM PRODUÇÃO:")
        print(f"   Total de turmas: {len(turmas)}")
        
        # Listar as 10 primeiras para comparar
        print(f"\n   Primeiras 10 turmas:")
        for i, t in enumerate(turmas[:10], 1):
            print(f"   {i}. {t['nome']}")
        
        # Ver se tem duplicatas
        nomes = [t['nome'] for t in turmas]
        duplicatas = [nome for nome in set(nomes) if nomes.count(nome) > 1]
        
        if duplicatas:
            print(f"\n⚠️  DUPLICATAS ENCONTRADAS:")
            for dup in duplicatas:
                count = nomes.count(dup)
                print(f"   '{dup}' aparece {count}x")
        else:
            print(f"\n✅ Nenhuma duplicata encontrada")
        
        # Verificar estrutura de uma turma
        if turmas:
            print(f"\n📋 ESTRUTURA DE UMA TURMA (primeira):")
            primeira = turmas[0]
            for key in primeira.keys():
                value = primeira[key]
                if isinstance(value, list):
                    print(f"   {key}: [{len(value)} itens]")
                elif isinstance(value, str) and len(value) > 50:
                    print(f"   {key}: {value[:50]}...")
                else:
                    print(f"   {key}: {value}")

if __name__ == "__main__":
    asyncio.run(descobrir_configuracao_render())
