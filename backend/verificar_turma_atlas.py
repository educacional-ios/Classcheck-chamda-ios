import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from urllib.parse import quote_plus

async def verificar_turma_barreiro():
    username = quote_plus("educacional_db_user")
    password = quote_plus("qpvR7mlOHSoxwvQ8")
    
    MONGO_URL = f"mongodb+srv://{username}:{password}@chamada-prod.nr10evs.mongodb.net/IOS-SISTEMA-CHAMADA?retryWrites=true&w=majority&appName=chamada-prod"
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client["IOS-SISTEMA-CHAMADA"]
    
    print("\n🔍 Verificando turma Barreiro BH Manhã T1 no MongoDB Atlas...\n")
    
    turma = await db.turmas.find_one({"nome": {"$regex": "Barreiro BH Manhã T1", "$options": "i"}})
    
    if turma:
        print(f"✅ Turma encontrada:")
        print(f"   Nome: {turma.get('nome')}")
        print(f"   ID: {turma.get('id')}")
        print(f"   instrutor_ids: {turma.get('instrutor_ids', 'CAMPO NÃO EXISTE')}")
        print(f"   instrutor_id (antigo): {turma.get('instrutor_id', 'AUSENTE')}")
        
        # Contar turmas com instrutores
        total_com_instrutor = await db.turmas.count_documents({"instrutor_ids": {"$exists": True, "$ne": []}})
        total_sem_instrutor = await db.turmas.count_documents({"$or": [{"instrutor_ids": {"$exists": False}}, {"instrutor_ids": []}]})
        
        print(f"\n📊 Estatísticas:")
        print(f"   Turmas COM instrutores: {total_com_instrutor}")
        print(f"   Turmas SEM instrutores: {total_sem_instrutor}")
    else:
        print("❌ Turma não encontrada no MongoDB Atlas")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(verificar_turma_barreiro())
