#!/usr/bin/env python3
"""
Listar as 5 turmas mais recentes
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

MONGO_URI = "mongodb+srv://educacional_db_user:qpvR7mlOHSoxwvQ8@chamada-prod.nr10evs.mongodb.net/?retryWrites=true&w=majority&appName=chamada-prod"
DB_NAME = "IOS-SISTEMA-CHAMADA"

async def listar_turmas_recentes():
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]
    
    print("=" * 80)
    print("5 TURMAS MAIS RECENTES")
    print("=" * 80)
    
    # Buscar turmas ordenadas por created_at
    turmas = await db.turmas.find().sort("created_at", -1).limit(5).to_list(5)
    
    for i, turma in enumerate(turmas, 1):
        print(f"\n{i}. {turma.get('nome')}")
        print(f"   ID: {turma.get('id')}")
        print(f"   Ciclo: {turma.get('ciclo')}")
        print(f"   Criada em: {turma.get('created_at')}")
        
        if 'instrutor_id' in turma:
            print(f"   ❌ instrutor_id (antigo): {turma['instrutor_id']}")
        
        if 'instrutor_ids' in turma:
            instrutor_ids = turma['instrutor_ids']
            print(f"   ✅ instrutor_ids (novo): {instrutor_ids}")
            print(f"   📊 {len(instrutor_ids)} instrutor(es)")
            
            for j, instrutor_id in enumerate(instrutor_ids, 1):
                usuario = await db.usuarios.find_one({"id": instrutor_id})
                if usuario:
                    print(f"      {j}. {usuario.get('nome')}")
        
        print(f"   Ativo: {turma.get('ativo', False)}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(listar_turmas_recentes())
