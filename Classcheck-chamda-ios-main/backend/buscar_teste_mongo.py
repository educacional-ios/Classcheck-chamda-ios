#!/usr/bin/env python3
"""
Buscar turma Teste no MongoDB
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = "mongodb+srv://educacional_db_user:qpvR7mlOHSoxwvQ8@chamada-prod.nr10evs.mongodb.net/?retryWrites=true&w=majority&appName=chamada-prod"
DB_NAME = "IOS-SISTEMA-CHAMADA"

async def buscar():
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]
    
    # Buscar qualquer turma com nome "Teste"
    turma = await db.turmas.find_one({"nome": "Teste"})
    
    if turma:
        print("TURMA ENCONTRADA:")
        print(f"ID: {turma.get('id')}")
        print(f"Nome: {turma.get('nome')}")
        
        # Mostrar TODOS os campos de instrutor
        print("\nCAMPOS DE INSTRUTOR:")
        for key in turma.keys():
            if 'instrutor' in key.lower():
                print(f"  {key}: {turma[key]}")
        
        # Ver instrutor_ids especificamente
        if 'instrutor_ids' in turma:
            ids = turma['instrutor_ids']
            print(f"\n✅ instrutor_ids: {ids}")
            print(f"   Quantidade: {len(ids)}")
            
            # Nomes
            for i, uid in enumerate(ids, 1):
                u = await db.usuarios.find_one({"id": uid})
                if u:
                    print(f"   {i}. {u['nome']}")
        else:
            print("\n❌ Campo instrutor_ids NÃO existe!")
    else:
        print("❌ Turma não encontrada")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(buscar())
