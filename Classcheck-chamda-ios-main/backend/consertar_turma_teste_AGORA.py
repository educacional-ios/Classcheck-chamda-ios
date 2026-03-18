#!/usr/bin/env python3
"""
SOLUÇÃO IMEDIATA: Adicionar Raissa na turma Teste DIRETO NO MONGODB
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = "mongodb+srv://educacional_db_user:qpvR7mlOHSoxwvQ8@chamada-prod.nr10evs.mongodb.net/?retryWrites=true&w=majority&appName=chamada-prod"
DB_NAME = "IOS-SISTEMA-CHAMADA"

TURMA_ID = "df4ac84b-99ce-46fc-af90-31e948764479"  # ID da turma Teste
IAGO_ID = "03dea76b-9932-4240-982b-bf406bb3f003"
RAISSA_ID = "41082b8d-4359-4fdd-a5e2-98c54871bf31"

async def consertar_turma_teste():
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]
    
    print("🔧 CONSERTANDO TURMA TESTE - ADICIONANDO 2 INSTRUTORES")
    print("=" * 80)
    
    # Atualizar turma: remover instrutor_id e adicionar instrutor_ids com 2 instrutores
    result = await db.turmas.update_one(
        {"id": TURMA_ID},
        {
            "$set": {"instrutor_ids": [IAGO_ID, RAISSA_ID]},
            "$unset": {"instrutor_id": ""}
        }
    )
    
    if result.modified_count > 0:
        print("✅ Turma atualizada com sucesso!")
        
        # Verificar
        turma = await db.turmas.find_one({"id": TURMA_ID})
        print(f"\nVerificação:")
        print(f"  instrutor_ids: {turma.get('instrutor_ids')}")
        print(f"  Tem instrutor_id (antigo)?: {'instrutor_id' in turma}")
        
        if len(turma.get('instrutor_ids', [])) == 2:
            print("\n🎉 SUCESSO! Turma agora tem 2 instrutores!")
            print("\n✅ Teste agora:")
            print("   1. Faça login como Iago (iago.herbert@ios.org.br / b99018cd)")
            print("   2. Veja se a turma Teste aparece")
            print("   3. Faça login como Raissa (raissa.pinho@ios.org.br / b99018cd)")
            print("   4. Veja se a turma Teste aparece para ela também")
        else:
            print(f"\n❌ Algo deu errado. instrutor_ids: {turma.get('instrutor_ids')}")
    else:
        print("❌ Nenhuma turma foi atualizada. Turma não encontrada?")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(consertar_turma_teste())
