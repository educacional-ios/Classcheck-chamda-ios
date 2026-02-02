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

print("🔍 VERIFICANDO CAMPOS DAS 3 USUÁRIAS:\n")

for email in emails:
    usuario = db.usuarios.find_one({"email": email})
    if usuario:
        print(f"📧 {email}")
        print(f"   Nome: {usuario.get('nome')}")
        print(f"   Tipo: {usuario.get('tipo')}")
        print(f"   Ativo: {usuario.get('ativo')}")
        print(f"   Status: {usuario.get('status')} ⚠️")
        print(f"   ID: {usuario.get('id')}")
        print(f"   Campos disponíveis: {list(usuario.keys())}")
        print()

print("\n📊 COMPARANDO COM USUÁRIO QUE APARECE NA API:\n")
usuario_ok = db.usuarios.find_one({"email": "iago.santos@ios.org.br"})
if usuario_ok:
    print(f"📧 iago.santos@ios.org.br (APARECE NA API)")
    print(f"   Status: {usuario_ok.get('status')}")
    print(f"   Ativo: {usuario_ok.get('ativo')}")
    print(f"   Campos: {list(usuario_ok.keys())}")

client.close()
