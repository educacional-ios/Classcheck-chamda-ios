from pymongo import MongoClient
from urllib.parse import quote_plus
from passlib.hash import bcrypt

# Conexão MongoDB Atlas
username = quote_plus("educacional_db_user")
password = quote_plus("qpvR7mlOHSoxwvQ8")

MONGO_URL = f"mongodb+srv://{username}:{password}@chamada-prod.nr10evs.mongodb.net/IOS-SISTEMA-CHAMADA?retryWrites=true&w=majority&appName=chamada-prod"
DB_NAME = "IOS-SISTEMA-CHAMADA"

client = MongoClient(MONGO_URL)
db = client[DB_NAME]

print("🔌 Conectando ao MongoDB Atlas...")
client.admin.command('ping')
print("✅ Conectado!\n")

# Buscar todos os usuários
usuarios = list(db.usuarios.find({}).sort("nome", 1))

print("🔐 VOLTANDO PARA O PADRÃO ANTIGO: IOS@2026\n")
print("=" * 130)

dados_usuarios = []

for user in usuarios:
    nome = user.get('nome', '')
    email = user.get('email', '')
    user_id = user.get('id')
    
    # PADRÃO ANTIGO: IOS@2026 (senha fixa para todos)
    senha_padrao = "IOS@2026"
    senha_hash = bcrypt.hash(senha_padrao)
    
    # Atualizar no banco
    db.usuarios.update_one(
        {"id": user_id},
        {"$set": {
            "senha": senha_hash,
            "primeiro_acesso": True
        }}
    )
    
    print(f"✅ {nome:<40} → {senha_padrao}")

print("=" * 130)
print(f"\n📊 Total de usuários atualizados: {len(usuarios)}")
print("\n✅ TODAS AS SENHAS FORAM REDEFINIDAS PARA: IOS@2026")
print("=" * 130)

client.close()
