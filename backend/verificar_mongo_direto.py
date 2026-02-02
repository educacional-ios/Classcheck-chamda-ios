#!/usr/bin/env python3
"""
Verificar DIRETAMENTE no MongoDB Atlas se os documentos foram migrados
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = "mongodb+srv://educacional_db_user:qpvR7mlOHSoxwvQ8@chamada-prod.nr10evs.mongodb.net/?retryWrites=true&w=majority&appName=chamada-prod"
DB_NAME = "IOS-SISTEMA-CHAMADA"

async def verificar_migracao():
    """Verifica se documentos foram migrados"""
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]
    
    print("=" * 80)
    print("VERIFICANDO DOCUMENTOS DIRETAMENTE NO MONGODB")
    print("=" * 80)
    
    # Buscar turma Barreiro
    turma_barreiro = await db.turmas.find_one({"nome": {"$regex": "Barreiro", "$options": "i"}})
    
    if turma_barreiro:
        print("\n✅ Turma Barreiro encontrada:")
        print(f"   ID: {turma_barreiro.get('id')}")
        print(f"   Nome: {turma_barreiro.get('nome')}")
        print(f"   Tem campo 'instrutor_id' (ANTIGO): {'instrutor_id' in turma_barreiro}")
        print(f"   Tem campo 'instrutor_ids' (NOVO): {'instrutor_ids' in turma_barreiro}")
        
        if 'instrutor_id' in turma_barreiro:
            print(f"   ❌ VALOR instrutor_id: {turma_barreiro['instrutor_id']}")
        if 'instrutor_ids' in turma_barreiro:
            print(f"   ✅ VALOR instrutor_ids: {turma_barreiro['instrutor_ids']}")
    else:
        print("\n❌ Turma Barreiro NÃO encontrada")
    
    # Estatísticas gerais
    print("\n" + "=" * 80)
    print("ESTATÍSTICAS GERAIS:")
    print("=" * 80)
    
    total_turmas = await db.turmas.count_documents({})
    com_instrutor_id = await db.turmas.count_documents({"instrutor_id": {"$exists": True}})
    com_instrutor_ids = await db.turmas.count_documents({"instrutor_ids": {"$exists": True}})
    
    print(f"\n📊 Total de turmas: {total_turmas}")
    print(f"❌ Com campo instrutor_id (antigo): {com_instrutor_id}")
    print(f"✅ Com campo instrutor_ids (novo): {com_instrutor_ids}")
    
    # Mostrar 3 exemplos de documentos
    print("\n" + "=" * 80)
    print("EXEMPLOS DE DOCUMENTOS (3 primeiras turmas):")
    print("=" * 80)
    
    async for turma in db.turmas.find().limit(3):
        print(f"\n📋 Turma: {turma.get('nome', 'SEM NOME')}")
        print(f"   ID: {turma.get('id')}")
        print(f"   Tem 'instrutor_id': {'instrutor_id' in turma}")
        print(f"   Tem 'instrutor_ids': {'instrutor_ids' in turma}")
        if 'instrutor_id' in turma:
            print(f"   Valor instrutor_id: {turma['instrutor_id']}")
        if 'instrutor_ids' in turma:
            print(f"   Valor instrutor_ids: {turma['instrutor_ids']}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(verificar_migracao())
