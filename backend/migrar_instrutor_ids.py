import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from urllib.parse import quote_plus

# Credenciais
username = quote_plus("educacional_db_user")
password = quote_plus("qpvR7mlOHSoxwvQ8")

MONGO_URL = f"mongodb+srv://{username}:{password}@chamada-prod.nr10evs.mongodb.net/IOS-SISTEMA-CHAMADA?retryWrites=true&w=majority&appName=chamada-prod"
DB_NAME = "IOS-SISTEMA-CHAMADA"

async def migrar():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("🔄 INICIANDO MIGRAÇÃO DE instrutor_id PARA instrutor_ids")
    print("=" * 80)
    
    # Buscar todas as turmas que ainda têm instrutor_id
    turmas = await db.turmas.find({"instrutor_id": {"$exists": True}}).to_list(1000)
    
    print(f"📊 Encontradas {len(turmas)} turmas com campo antigo 'instrutor_id'")
    
    migradas = 0
    for turma in turmas:
        turma_id = turma.get('id')
        instrutor_id_antigo = turma.get('instrutor_id')
        instrutor_ids_existente = turma.get('instrutor_ids', [])
        
        print(f"\n📚 Turma: {turma.get('nome')}")
        print(f"   instrutor_id (antigo): {instrutor_id_antigo}")
        print(f"   instrutor_ids (atual): {instrutor_ids_existente}")
        
        # Criar novo array
        if not instrutor_ids_existente:
            # Se não tem instrutor_ids, criar com o valor do instrutor_id antigo
            novo_array = [instrutor_id_antigo] if instrutor_id_antigo else []
        else:
            # Se já tem instrutor_ids, manter e garantir que o antigo esteja lá
            novo_array = instrutor_ids_existente
            if instrutor_id_antigo and instrutor_id_antigo not in novo_array:
                novo_array.append(instrutor_id_antigo)
        
        # Atualizar no banco
        result = await db.turmas.update_one(
            {"id": turma_id},
            {
                "$set": {"instrutor_ids": novo_array},
                "$unset": {"instrutor_id": ""}  # Remover campo antigo
            }
        )
        
        if result.modified_count > 0:
            print(f"   ✅ Migrada para: {novo_array}")
            migradas += 1
        else:
            print(f"   ⚠️  Não foi necessário alterar")
    
    print("\n" + "=" * 80)
    print(f"✅ MIGRAÇÃO CONCLUÍDA: {migradas} turmas atualizadas")
    print("=" * 80)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(migrar())
