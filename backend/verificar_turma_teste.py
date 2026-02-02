#!/usr/bin/env python3
"""
Verificar se a turma Teste foi criada com 2 instrutores
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = "mongodb+srv://educacional_db_user:qpvR7mlOHSoxwvQ8@chamada-prod.nr10evs.mongodb.net/?retryWrites=true&w=majority&appName=chamada-prod"
DB_NAME = "IOS-SISTEMA-CHAMADA"

async def verificar_turma_teste():
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]
    
    print("=" * 80)
    print("VERIFICANDO TURMA 'Teste' COM 2 INSTRUTORES")
    print("=" * 80)
    
    # Buscar turma Teste
    turma = await db.turmas.find_one({"nome": "Teste"})
    
    if turma:
        print(f"\n✅ Turma encontrada!")
        print(f"   ID: {turma.get('id')}")
        print(f"   Nome: {turma.get('nome')}")
        print(f"   Ciclo: {turma.get('ciclo')}")
        
        # Verificar campos de instrutor
        if 'instrutor_id' in turma:
            print(f"   ⚠️ Campo antigo 'instrutor_id': {turma['instrutor_id']}")
        
        if 'instrutor_ids' in turma:
            instrutor_ids = turma['instrutor_ids']
            print(f"   ✅ Campo novo 'instrutor_ids': {instrutor_ids}")
            print(f"   📊 Quantidade de instrutores: {len(instrutor_ids)}")
            
            # Buscar nomes dos instrutores
            for i, instrutor_id in enumerate(instrutor_ids, 1):
                usuario = await db.usuarios.find_one({"id": instrutor_id})
                if usuario:
                    print(f"   👤 Instrutor {i}: {usuario.get('nome')} ({usuario.get('email')})")
            
            if len(instrutor_ids) == 2:
                print(f"\n🎉 SUCESSO! Turma tem 2 instrutores!")
            elif len(instrutor_ids) == 1:
                print(f"\n⚠️ ATENÇÃO: Turma tem apenas 1 instrutor")
            else:
                print(f"\n❌ ERRO: Turma tem {len(instrutor_ids)} instrutores")
        else:
            print(f"   ❌ Campo 'instrutor_ids' NÃO existe!")
    else:
        print("\n❌ Turma 'Teste' não encontrada")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(verificar_turma_teste())
