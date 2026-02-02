import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from urllib.parse import quote_plus

async def listar_todos_databases():
    username = quote_plus("educacional_db_user")
    password = quote_plus("qpvR7mlOHSoxwvQ8")
    
    MONGO_URL = f"mongodb+srv://{username}:{password}@chamada-prod.nr10evs.mongodb.net/?retryWrites=true&w=majority&appName=chamada-prod"
    
    client = AsyncIOMotorClient(MONGO_URL)
    
    print("\n" + "="*60)
    print("🔍 LISTANDO TODOS OS DATABASES NO CLUSTER")
    print("="*60 + "\n")
    
    # Listar todos os databases
    db_list = await client.list_database_names()
    
    print(f"📊 Databases encontrados: {len(db_list)}\n")
    
    for db_name in db_list:
        print(f"\n📂 Database: {db_name}")
        print("-" * 40)
        
        db = client[db_name]
        collections = await db.list_collection_names()
        
        print(f"   Coleções ({len(collections)}):")
        for coll_name in collections:
            count = await db[coll_name].count_documents({})
            print(f"      • {coll_name}: {count} documentos")
            
            # Se for coleção 'turmas', mostrar mais detalhes
            if coll_name == "turmas":
                print(f"         🔍 Analisando turmas...")
                turmas = await db[coll_name].find({}).to_list(5)
                for i, turma in enumerate(turmas[:3], 1):
                    print(f"            {i}. {turma.get('nome', 'SEM NOME')}")
    
    print("\n" + "="*60)
    print("✅ VERIFICAÇÃO CONCLUÍDA")
    print("="*60 + "\n")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(listar_todos_databases())
