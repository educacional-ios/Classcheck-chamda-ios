import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def contar_turmas():
    # Conexão
    MONGODB_URL = "mongodb+srv://educacional_db_user:qpvR7mlOHSoxwvQ8@chamada-prod.nr10evs.mongodb.net/IOS-SISTEMA-CHAMADA?retryWrites=true&w=majority&appName=chamada-prod"
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client["IOS-SISTEMA-CHAMADA"]
    
    # Contar de várias formas
    total_count = await db.turmas.count_documents({})
    print(f"📊 count_documents({{}}): {total_count}")
    
    total_list = await db.turmas.find({}).to_list(None)
    print(f"📊 find({{}}).to_list(None): {len(total_list)}")
    
    # Verificar se há filtros na coleção
    indexes = await db.turmas.list_indexes().to_list(None)
    print(f"\n🔍 Índices na coleção:")
    for idx in indexes:
        print(f"   - {idx}")
    
    # Mostrar algumas turmas para debug
    print(f"\n📋 Primeiras 5 turmas:")
    for i, turma in enumerate(total_list[:5]):
        print(f"\n{i+1}. {turma.get('nome', 'SEM NOME')}")
        print(f"   ID: {turma.get('id', 'SEM ID')}")
        print(f"   instrutor_id: {turma.get('instrutor_id', 'AUSENTE')}")
        print(f"   instrutor_ids: {turma.get('instrutor_ids', 'AUSENTE')}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(contar_turmas())
