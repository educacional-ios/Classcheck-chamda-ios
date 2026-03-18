import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME")

async def verificar_detalhado():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print(f"\n🔍 Verificação Detalhada - Banco: {DB_NAME}\n")
    print("="*80)
    
    # Buscar todas as turmas SEM filtro
    all_turmas = await db.turmas.find({}).to_list(1000)
    print(f"\n📊 TOTAL DE TURMAS (sem filtro): {len(all_turmas)}")
    
    # Buscar turmas ativas
    turmas_ativas = await db.turmas.find({"ativo": True}).to_list(1000)
    print(f"📊 TURMAS ATIVAS (ativo=True): {len(turmas_ativas)}")
    
    # Buscar turmas inativas
    turmas_inativas = await db.turmas.find({"ativo": False}).to_list(1000)
    print(f"📊 TURMAS INATIVAS (ativo=False): {len(turmas_inativas)}")
    
    print("\n" + "="*80)
    print("\n📋 LISTAGEM COMPLETA DE TODAS AS TURMAS:\n")
    
    for i, turma in enumerate(all_turmas, 1):
        nome = turma.get('nome', 'SEM NOME')
        ativo = turma.get('ativo', 'N/A')
        tipo = turma.get('tipo_turma', 'N/A')
        
        # Buscar nome da unidade
        unidade_id = turma.get('unidade_id')
        unidade = await db.unidades.find_one({"id": unidade_id})
        unidade_nome = unidade.get('nome') if unidade else 'UNIDADE NÃO ENCONTRADA'
        
        status_icon = "✅" if ativo == True else "❌" if ativo == False else "⚠️"
        
        print(f"{i}. {status_icon} {nome}")
        print(f"   Unidade: {unidade_nome}")
        print(f"   Ativo: {ativo}")
        print(f"   Tipo: {tipo}")
        print(f"   ID: {turma.get('id', 'N/A')}")
        print()
    
    # Verificar se há algum campo diferente
    print("="*80)
    print("\n🔍 VERIFICANDO ESTRUTURA DAS TURMAS:\n")
    
    if all_turmas:
        primeira_turma = all_turmas[0]
        print("Campos da primeira turma:")
        for key in primeira_turma.keys():
            print(f"   - {key}: {type(primeira_turma[key])}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(verificar_detalhado())
