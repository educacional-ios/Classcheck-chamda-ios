import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")

async def listar_todos_bancos():
    client = AsyncIOMotorClient(MONGO_URL)
    
    print(f"\n🔍 Conectando em: {MONGO_URL[:80]}...\n")
    print("="*80)
    
    # Listar TODOS os bancos de dados no cluster
    bancos = await client.list_database_names()
    
    print(f"\n📚 TODOS OS BANCOS DE DADOS NO CLUSTER:\n")
    for banco_nome in bancos:
        if banco_nome not in ['admin', 'local', 'config']:
            db = client[banco_nome]
            
            # Contar turmas em cada banco
            try:
                turmas_count = await db.turmas.count_documents({})
                print(f"\n📦 Banco: {banco_nome}")
                print(f"   Turmas: {turmas_count}")
                
                if turmas_count > 0:
                    # Listar nomes das turmas
                    turmas = await db.turmas.find({}, {"nome": 1, "_id": 0}).limit(5).to_list(5)
                    print(f"   Exemplos:")
                    for t in turmas:
                        print(f"      - {t.get('nome', 'SEM NOME')}")
            except Exception as e:
                print(f"   Erro ao acessar: {e}")
    
    print("\n" + "="*80)
    client.close()

if __name__ == "__main__":
    asyncio.run(listar_todos_bancos())
