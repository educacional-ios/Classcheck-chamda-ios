#!/usr/bin/env python3
"""
Script para criar índices únicos necessários para o sistema de attendance
Execute este script UMA VEZ após fazer deploy do backend
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

async def create_attendance_indexes():
    """Criar índices únicos para a collection attendances"""
    
    # Configuração MongoDB
    mongo_url = os.environ.get('MONGO_URL')
    db_name = os.environ.get('DB_NAME', 'ios_sistema')
    
    if not mongo_url:
        print("❌ MONGO_URL não encontrada no .env")
        return
    
    # Conectar ao MongoDB
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    try:
        print(f"🔗 Conectando ao MongoDB: {db_name}")
        
        # 1) Índice único para impedir duplicação de presença por turma/data
        print("📋 Criando índice único (turma_id, data)...")
        result1 = await db.attendances.create_index(
            [("turma_id", 1), ("data", 1)], 
            unique=True,
            name="unique_turma_data"
        )
        print(f"✅ Índice único criado: {result1}")
        
        # 2) Índice para consultas rápidas por turma
        print("📋 Criando índice por turma_id...")
        result2 = await db.attendances.create_index([("turma_id", 1)])
        print(f"✅ Índice turma_id criado: {result2}")
        
        # 3) Índice para consultas rápidas nas turmas por instrutor
        print("📋 Criando índice instrutor_id em classes...")
        result3 = await db.classes.create_index([("instrutor_id", 1)])
        print(f"✅ Índice instrutor_id criado: {result3}")
        
        # 4) Verificar se os índices foram criados
        print("\n📊 Verificando índices criados:")
        
        # Listar índices da collection attendances
        attendance_indexes = await db.attendances.list_indexes().to_list(None)
        print("\n🔍 Índices em attendances:")
        for idx in attendance_indexes:
            print(f"   - {idx['name']}: {idx.get('key', 'N/A')}")
        
        # Listar índices da collection classes  
        classes_indexes = await db.classes.list_indexes().to_list(None)
        print("\n🔍 Índices em classes:")
        for idx in classes_indexes:
            print(f"   - {idx['name']}: {idx.get('key', 'N/A')}")
        
        print("\n🎉 Todos os índices foram criados com sucesso!")
        print("⚠️  IMPORTANTE: Execute este script apenas UMA VEZ")
        
    except Exception as e:
        print(f"❌ Erro ao criar índices: {e}")
        
    finally:
        # Fechar conexão
        client.close()
        print("🔌 Conexão MongoDB fechada")

if __name__ == "__main__":
    print("🚀 Iniciando criação de índices para sistema de attendance...")
    print("=" * 60)
    asyncio.run(create_attendance_indexes())
    print("=" * 60)
    print("✅ Script concluído!")