import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from urllib.parse import quote_plus

# Credenciais diretas
username = quote_plus("educacional_db_user")
password = quote_plus("qpvR7mlOHSoxwvQ8")

MONGO_URL = f"mongodb+srv://{username}:{password}@chamada-prod.nr10evs.mongodb.net/IOS-SISTEMA-CHAMADA?retryWrites=true&w=majority&appName=chamada-prod"
DB_NAME = "IOS-SISTEMA-CHAMADA"

async def verificar_turmas():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("=" * 80)
    print("🔍 VERIFICANDO TURMAS COM BARREIRO NO NOME")
    print("=" * 80)
    
    # Buscar turmas com "Barreiro" no nome
    turmas = await db.turmas.find({"nome": {"$regex": "Barreiro", "$options": "i"}}).to_list(100)
    
    for turma in turmas:
        print(f"\n📚 TURMA: {turma.get('nome')}")
        print(f"   ID: {turma.get('id')}")
        print(f"   Ativa: {turma.get('ativo')}")
        
        # Verificar se tem instrutor_id (antigo) ou instrutor_ids (novo)
        if 'instrutor_id' in turma:
            print(f"   ⚠️  TEM CAMPO ANTIGO 'instrutor_id': {turma.get('instrutor_id')}")
        
        if 'instrutor_ids' in turma:
            print(f"   ✅ TEM CAMPO NOVO 'instrutor_ids': {turma.get('instrutor_ids')}")
        else:
            print(f"   ❌ NÃO TEM CAMPO 'instrutor_ids'")
        
        # Mostrar todos os campos relacionados a instrutor
        print(f"\n   📋 Todos os campos da turma:")
        for key, value in turma.items():
            if 'instrutor' in key.lower() or 'pedagogo' in key.lower() or 'monitor' in key.lower():
                print(f"      {key}: {value}")
    
    print("\n" + "=" * 80)
    print("🔍 BUSCANDO USUÁRIOS IAGO E RAISSA")
    print("=" * 80)
    
    usuarios = await db.usuarios.find({
        "$or": [
            {"nome": {"$regex": "Iago", "$options": "i"}},
            {"nome": {"$regex": "Raissa", "$options": "i"}}
        ]
    }).to_list(100)
    
    user_ids = {}
    for user in usuarios:
        print(f"\n👤 {user.get('nome')}")
        print(f"   ID: {user.get('id')}")
        print(f"   Email: {user.get('email')}")
        print(f"   Tipo: {user.get('tipo')}")
        user_ids[user.get('nome')] = user.get('id')
    
    # Agora buscar TODAS as turmas e verificar quais tem esses IDs
    print("\n" + "=" * 80)
    print("🔍 BUSCANDO TURMAS QUE TENHAM IAGO OU RAISSA")
    print("=" * 80)
    
    todas_turmas = await db.turmas.find({}).to_list(1000)
    
    for turma in todas_turmas:
        # Verificar se tem instrutor_id ou instrutor_ids
        tem_iago_ou_raissa = False
        
        if 'instrutor_id' in turma:
            if turma['instrutor_id'] in user_ids.values():
                tem_iago_ou_raissa = True
        
        if 'instrutor_ids' in turma:
            for uid in user_ids.values():
                if uid in turma['instrutor_ids']:
                    tem_iago_ou_raissa = True
                    break
        
        if tem_iago_ou_raissa:
            print(f"\n📚 TURMA: {turma.get('nome')}")
            print(f"   ID: {turma.get('id')}")
            if 'instrutor_id' in turma:
                print(f"   ⚠️  instrutor_id (antigo): {turma.get('instrutor_id')}")
            if 'instrutor_ids' in turma:
                print(f"   ✅ instrutor_ids (novo): {turma.get('instrutor_ids')}")
            else:
                print(f"   ❌ NÃO TEM instrutor_ids")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(verificar_turmas())
