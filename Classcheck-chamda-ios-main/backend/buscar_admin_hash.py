from pymongo import MongoClient
from urllib.parse import quote_plus

# Credenciais do banco (conforme CREDENCIAIS_SISTEMA.txt)
username = quote_plus("educacional_db_user")
password = quote_plus("qpvR7mlOHSoxwvQ8")
MONGO_URL = f"mongodb+srv://{username}:{password}@chamada-prod.nr10evs.mongodb.net/IOS-SISTEMA-CHAMADA?retryWrites=true&w=majority&appName=chamada-prod"
DB_NAME = "IOS-SISTEMA-CHAMADA"

client = MongoClient(MONGO_URL)
db = client[DB_NAME]

# Buscar usuário admin pelo email documentado
admin_email = "jesiel.junior@ios.org.br"
admin = db.usuarios.find_one({"email": admin_email})

if admin:
    print(f"Usuário admin encontrado: {admin.get('nome')}")
    print(f"Email: {admin.get('email')}")
    print(f"Hash da senha: {admin.get('senha')}")
    print(f"Tipo: {admin.get('tipo')}")
else:
    print("Usuário admin não encontrado.")
