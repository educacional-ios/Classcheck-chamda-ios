from pymongo import MongoClient
from urllib.parse import quote_plus

# Conexão MongoDB Atlas
username = quote_plus("educacional_db_user")
password = quote_plus("qpvR7mlOHSoxwvQ8")

MONGO_URL = f"mongodb+srv://{username}:{password}@chamada-prod.nr10evs.mongodb.net/IOS-SISTEMA-CHAMADA?retryWrites=true&w=majority&appName=chamada-prod"
DB_NAME = "IOS-SISTEMA-CHAMADA"

client = MongoClient(MONGO_URL)
db = client[DB_NAME]

emails = [
    "fabiana.coelho@ios.org.br",
    "juliete.pereira@ios.org.br",
    "luana.soares@ios.org.br"
]

print("🔧 CORRIGINDO STATUS DAS 3 USUÁRIAS...\n")

for email in emails:
    resultado = db.usuarios.update_one(
        {"email": email},
        {"$set": {"status": "ativo"}}
    )
    
    if resultado.modified_count > 0:
        print(f"✅ {email} - Status atualizado para 'ativo'")
    else:
        print(f"⚠️ {email} - Nenhuma alteração necessária")

print("\n🔍 VERIFICANDO ALTERAÇÕES:\n")

for email in emails:
    usuario = db.usuarios.find_one({"email": email})
    if usuario:
        print(f"✅ {usuario.get('nome')}")
        print(f"   Status: {usuario.get('status')}")
        print()

client.close()

print("✅ PRONTO! Agora as 3 usuárias devem aparecer na API.")
