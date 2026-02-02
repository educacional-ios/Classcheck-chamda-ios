import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
import json

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME")

async def verificar_turmas():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print(f"\n🔍 Verificando turmas no banco: {DB_NAME}\n")
    
    # Buscar todas as turmas
    turmas = await db.turmas.find().to_list(1000)
    
    print(f"📊 Total de turmas encontradas: {len(turmas)}\n")
    print("="*80)
    
    for i, turma in enumerate(turmas, 1):
        print(f"\n{i}. {turma.get('nome', 'SEM NOME')}")
        print(f"   ID: {turma.get('id', 'N/A')}")
        print(f"   Unidade ID: {turma.get('unidade_id', 'N/A')}")
        print(f"   Curso ID: {turma.get('curso_id', 'N/A')}")
        print(f"   Instrutor ID: {turma.get('instrutor_id', 'N/A')}")
        print(f"   Tipo: {turma.get('tipo_turma', 'N/A')}")
        print(f"   Ativo: {turma.get('ativo', 'N/A')}")
        print(f"   Vagas: {turma.get('vagas_ocupadas', 0)}/{turma.get('vagas_total', 0)}")
        print(f"   Horário: {turma.get('horario_inicio', 'N/A')} - {turma.get('horario_fim', 'N/A')}")
        print(f"   Ciclo: {turma.get('ciclo', 'N/A')}")
        
        # Verificar se tem os campos necessários
        campos_obrigatorios = ['id', 'nome', 'unidade_id', 'curso_id', 'instrutor_id']
        campos_faltando = [c for c in campos_obrigatorios if not turma.get(c)]
        if campos_faltando:
            print(f"   ⚠️ CAMPOS FALTANDO: {campos_faltando}")
    
    # Agrupar por unidade
    print("\n" + "="*80)
    print("\n📍 TURMAS POR UNIDADE:")
    
    unidades = await db.unidades.find().to_list(1000)
    for unidade in unidades:
        turmas_unidade = [t for t in turmas if t.get('unidade_id') == unidade.get('id')]
        if turmas_unidade:
            print(f"\n   {unidade.get('nome')}: {len(turmas_unidade)} turmas")
            for t in turmas_unidade:
                print(f"      - {t.get('nome')}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(verificar_turmas())
