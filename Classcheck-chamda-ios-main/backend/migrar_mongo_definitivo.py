#!/usr/bin/env python3
"""
MIGRAÇÃO DEFINITIVA: instrutor_id → instrutor_ids DIRETAMENTE NO MONGODB
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = "mongodb+srv://educacional_db_user:qpvR7mlOHSoxwvQ8@chamada-prod.nr10evs.mongodb.net/?retryWrites=true&w=majority&appName=chamada-prod"
DB_NAME = "IOS-SISTEMA-CHAMADA"

async def migrar_definitivo():
    """Migra TODOS os documentos de forma definitiva"""
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]
    
    print("=" * 80)
    print("MIGRAÇÃO DEFINITIVA: instrutor_id → instrutor_ids")
    print("=" * 80)
    
    # 1. Contar turmas com campo antigo
    com_antigo = await db.turmas.count_documents({"instrutor_id": {"$exists": True}})
    print(f"\n📊 Turmas com campo 'instrutor_id' (antigo): {com_antigo}")
    
    if com_antigo == 0:
        print("\n✅ Nenhuma turma precisa de migração!")
        client.close()
        return
    
    # 2. Migrar TODAS as turmas com campo antigo
    print(f"\n🔄 Migrando {com_antigo} turmas...")
    
    migradas = 0
    erros = 0
    
    async for turma in db.turmas.find({"instrutor_id": {"$exists": True}}):
        try:
            turma_id = turma.get("id")
            instrutor_id_antigo = turma.get("instrutor_id")
            
            # Criar array com o instrutor existente
            instrutor_ids_novo = [instrutor_id_antigo] if instrutor_id_antigo else []
            
            # Update: adiciona instrutor_ids e remove instrutor_id
            result = await db.turmas.update_one(
                {"id": turma_id},
                {
                    "$set": {"instrutor_ids": instrutor_ids_novo},
                    "$unset": {"instrutor_id": ""}
                }
            )
            
            if result.modified_count > 0:
                migradas += 1
                print(f"   ✅ Migrada: {turma.get('nome', 'SEM NOME')[:50]}")
            
        except Exception as e:
            erros += 1
            print(f"   ❌ Erro: {str(e)}")
    
    print("\n" + "=" * 80)
    print("RESULTADO DA MIGRAÇÃO:")
    print("=" * 80)
    print(f"✅ Migradas com sucesso: {migradas}")
    print(f"❌ Erros: {erros}")
    
    # 3. Verificar resultado final
    com_antigo_depois = await db.turmas.count_documents({"instrutor_id": {"$exists": True}})
    com_novo_depois = await db.turmas.count_documents({"instrutor_ids": {"$exists": True}})
    total = await db.turmas.count_documents({})
    
    print(f"\n📊 APÓS MIGRAÇÃO:")
    print(f"   Total de turmas: {total}")
    print(f"   Com 'instrutor_id' (antigo): {com_antigo_depois}")
    print(f"   Com 'instrutor_ids' (novo): {com_novo_depois}")
    
    if com_antigo_depois == 0 and com_novo_depois == total:
        print("\n🎉 MIGRAÇÃO 100% CONCLUÍDA!")
    else:
        print("\n⚠️ ATENÇÃO: Migração incompleta")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(migrar_definitivo())
