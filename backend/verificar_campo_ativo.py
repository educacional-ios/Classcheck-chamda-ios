import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def verificar_campo_ativo():
    MONGODB_URL = "mongodb+srv://educacional_db_user:qpvR7mlOHSoxwvQ8@chamada-prod.nr10evs.mongodb.net/IOS-SISTEMA-CHAMADA?retryWrites=true&w=majority&appName=chamada-prod"
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client["IOS-SISTEMA-CHAMADA"]
    
    print("\n🔍 VERIFICANDO CAMPO 'ativo' NAS TURMAS\n")
    
    # Contar com ativo=True
    count_ativo_true = await db.turmas.count_documents({"ativo": True})
    print(f"✅ Turmas com ativo=True: {count_ativo_true}")
    
    # Contar com ativo=False
    count_ativo_false = await db.turmas.count_documents({"ativo": False})
    print(f"❌ Turmas com ativo=False: {count_ativo_false}")
    
    # Contar SEM campo ativo
    count_sem_ativo = await db.turmas.count_documents({"ativo": {"$exists": False}})
    print(f"⚠️  Turmas SEM campo 'ativo': {count_sem_ativo}")
    
    # Total
    count_total = await db.turmas.count_documents({})
    print(f"📊 Total de turmas: {count_total}")
    
    # Mostrar 5 exemplos
    print(f"\n📋 Primeiras 5 turmas (campo 'ativo'):")
    turmas = await db.turmas.find({}).limit(5).to_list(5)
    for i, turma in enumerate(turmas, 1):
        ativo_value = turma.get('ativo', 'CAMPO NÃO EXISTE')
        print(f"{i}. {turma.get('nome', 'SEM NOME')}")
        print(f"   ativo: {ativo_value}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(verificar_campo_ativo())
