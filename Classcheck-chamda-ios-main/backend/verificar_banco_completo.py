import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def verificar_banco_completo():
    MONGODB_URL = "mongodb+srv://educacional_db_user:qpvR7mlOHSoxwvQ8@chamada-prod.nr10evs.mongodb.net/IOS-SISTEMA-CHAMADA?retryWrites=true&w=majority&appName=chamada-prod"
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client["IOS-SISTEMA-CHAMADA"]
    
    print("\n" + "="*60)
    print("📊 VERIFICAÇÃO COMPLETA DO BANCO DE DADOS")
    print("="*60 + "\n")
    
    # Listar todas as coleções
    collections = await db.list_collection_names()
    print(f"📂 Coleções disponíveis: {collections}\n")
    
    # Contar documentos em cada coleção
    for collection_name in collections:
        count = await db[collection_name].count_documents({})
        print(f"   {collection_name}: {count} documentos")
    
    print("\n" + "="*60)
    print("📋 TURMAS DETALHADAS")
    print("="*60 + "\n")
    
    turmas = await db.turmas.find({}).to_list(None)
    print(f"Total: {len(turmas)} turmas\n")
    
    for i, turma in enumerate(turmas, 1):
        print(f"{i}. {turma.get('nome', 'SEM NOME')}")
        instrutor_ids = turma.get('instrutor_ids', [])
        instrutor_id_antigo = turma.get('instrutor_id', None)
        
        if instrutor_id_antigo:
            print(f"   ⚠️  CAMPO ANTIGO AINDA PRESENTE: instrutor_id={instrutor_id_antigo}")
        
        print(f"   instrutor_ids: {instrutor_ids} ({len(instrutor_ids) if isinstance(instrutor_ids, list) else 'NAO É ARRAY'})")
    
    print("\n" + "="*60)
    print("👥 USUÁRIOS POR TIPO")
    print("="*60 + "\n")
    
    usuarios = await db.usuarios.find({}).to_list(None)
    tipos = {}
    for user in usuarios:
        tipo = user.get('tipo', 'SEM TIPO')
        tipos[tipo] = tipos.get(tipo, 0) + 1
    
    for tipo, count in tipos.items():
        print(f"   {tipo}: {count}")
    
    # Encontrar Raissa
    print("\n" + "="*60)
    print("🔍 BUSCANDO RAISSA")
    print("="*60 + "\n")
    
    raissa = await db.usuarios.find_one({"nome": {"$regex": "raissa", "$options": "i"}})
    if raissa:
        print(f"✅ Encontrada: {raissa.get('nome')}")
        print(f"   ID: {raissa.get('id')}")
        print(f"   Tipo: {raissa.get('tipo')}")
        print(f"   Email: {raissa.get('email')}")
        
        # Verificar em quantas turmas está
        raissa_id = raissa.get('id')
        turmas_raissa = await db.turmas.find({"instrutor_ids": raissa_id}).to_list(None)
        print(f"\n   Turmas vinculadas: {len(turmas_raissa)}")
        for t in turmas_raissa:
            print(f"      - {t.get('nome')}")
    else:
        print("❌ Raissa não encontrada")
    
    # Buscar turma Barreiro
    print("\n" + "="*60)
    print("🔍 BUSCANDO TURMA BARREIRO")
    print("="*60 + "\n")
    
    barreiro = await db.turmas.find_one({"nome": {"$regex": "barreiro", "$options": "i"}})
    if barreiro:
        print(f"✅ Encontrada: {barreiro.get('nome')}")
        print(f"   ID: {barreiro.get('id')}")
        print(f"   instrutor_ids: {barreiro.get('instrutor_ids')}")
        print(f"   instrutor_id (antigo): {barreiro.get('instrutor_id', 'AUSENTE')}")
    else:
        print("❌ Turma Barreiro não encontrada")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(verificar_banco_completo())
