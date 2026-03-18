import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from urllib.parse import quote_plus

# Credenciais
username = quote_plus("educacional_db_user")
password = quote_plus("qpvR7mlOHSoxwvQ8")

MONGO_URL = f"mongodb+srv://{username}:{password}@chamada-prod.nr10evs.mongodb.net/IOS-SISTEMA-CHAMADA?retryWrites=true&w=majority&appName=chamada-prod"
DB_NAME = "IOS-SISTEMA-CHAMADA"

async def verificar_e_migrar_todas():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("🔄 VERIFICANDO E MIGRANDO TODAS AS TURMAS")
    print("=" * 80)
    
    # Buscar TODAS as turmas
    todas_turmas = await db.turmas.find({}).to_list(1000)
    
    print(f"📊 Total de turmas no banco: {len(todas_turmas)}")
    print("=" * 80)
    
    migradas = 0
    ja_corretas = 0
    
    for turma in todas_turmas:
        turma_id = turma.get('id')
        nome = turma.get('nome', 'SEM NOME')
        instrutor_id_antigo = turma.get('instrutor_id')
        instrutor_ids_atual = turma.get('instrutor_ids')
        
        # Determinar o que fazer
        precisa_migrar = False
        novo_array = []
        
        if instrutor_ids_atual is None:
            # NÃO TEM instrutor_ids, precisa criar
            if instrutor_id_antigo:
                novo_array = [instrutor_id_antigo]
                precisa_migrar = True
                print(f"\n❌ {nome}")
                print(f"   Tem instrutor_id: {instrutor_id_antigo}")
                print(f"   NÃO tem instrutor_ids - CRIANDO: {novo_array}")
            else:
                # Não tem nem um nem outro - criar vazio
                novo_array = []
                precisa_migrar = True
                print(f"\n⚠️  {nome}")
                print(f"   NÃO tem nenhum campo de instrutor - CRIANDO vazio")
        elif not isinstance(instrutor_ids_atual, list):
            # Tem instrutor_ids mas NÃO é array
            novo_array = [instrutor_ids_atual] if instrutor_ids_atual else []
            precisa_migrar = True
            print(f"\n⚠️  {nome}")
            print(f"   instrutor_ids NÃO é array: {instrutor_ids_atual}")
            print(f"   CONVERTENDO para: {novo_array}")
        else:
            # Já tem instrutor_ids como array
            ja_corretas += 1
            continue
        
        if precisa_migrar:
            # Atualizar no banco
            update_ops = {"$set": {"instrutor_ids": novo_array}}
            if instrutor_id_antigo:
                update_ops["$unset"] = {"instrutor_id": ""}
            
            result = await db.turmas.update_one(
                {"id": turma_id},
                update_ops
            )
            
            if result.modified_count > 0:
                print(f"   ✅ MIGRADA")
                migradas += 1
    
    print("\n" + "=" * 80)
    print(f"✅ MIGRAÇÃO CONCLUÍDA:")
    print(f"   Total de turmas: {len(todas_turmas)}")
    print(f"   Já estavam corretas: {ja_corretas}")
    print(f"   Migradas agora: {migradas}")
    print("=" * 80)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(verificar_e_migrar_todas())
