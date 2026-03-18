from pymongo import MongoClient
from urllib.parse import quote_plus
from passlib.hash import bcrypt
import uuid

# Configurações de conexão
username = quote_plus("educacional_db_user")
password = quote_plus("qpvR7mlOHSoxwvQ8")
MONGO_URL = f"mongodb+srv://{username}:{password}@chamada-prod.nr10evs.mongodb.net/IOS-SISTEMA-CHAMADA?retryWrites=true&w=majority&appName=chamada-prod"
DB_NAME = "IOS-SISTEMA-CHAMADA"

client = MongoClient(MONGO_URL)
db = client[DB_NAME]

email = "usuariopadrao@ios.com"
senha = "padrao123"
nome = "Usuário Padrão"
tipo = "admin"

print("🔌 Conectando ao MongoDB Atlas...")
try:
    client.admin.command('ping')
    print("✅ Conectado ao MongoDB Atlas com sucesso!\n")
except Exception as e:
    print(f"❌ Erro ao conectar: {e}")
    exit(1)

# Verifica se o usuário já existe
existe = db.usuarios.find_one({"email": email})
if existe:
    print(f"⚠️  Usuário '{email}' já existe no banco!")
else:
    senha_hash = bcrypt.hash(senha)
    novo_usuario = {
        "id": str(uuid.uuid4()),
        "nome": nome,
        "email": email,
        "senha": senha_hash,
        "tipo": tipo,
        "primeiro_acesso": True,
        "ativo": True,
        "unidade_id": None,
        "curso_id": None
    }
    db.usuarios.insert_one(novo_usuario)
    print(f"✅ Usuário criado: {email} | Senha: {senha}")

client.close()