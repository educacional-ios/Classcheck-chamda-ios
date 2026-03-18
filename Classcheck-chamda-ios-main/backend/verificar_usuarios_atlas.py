from pymongo import MongoClient
from urllib.parse import quote_plus

# Conexão MongoDB Atlas
username = quote_plus("educacional_db_user")
password = quote_plus("qpvR7mlOHSoxwvQ8")

MONGO_URL = f"mongodb+srv://{username}:{password}@chamada-prod.nr10evs.mongodb.net/IOS-SISTEMA-CHAMADA?retryWrites=true&w=majority&appName=chamada-prod"
DB_NAME = "IOS-SISTEMA-CHAMADA"

print("🔌 Conectando ao MongoDB Atlas...")
client = MongoClient(MONGO_URL)
db = client[DB_NAME]

try:
    client.admin.command('ping')
    print("✅ Conectado ao MongoDB Atlas com sucesso!\n")
except Exception as e:
    print(f"❌ Erro ao conectar: {e}")
    exit(1)

# Buscar TODOS os usuários
print("👥 Buscando todos os usuários no MongoDB Atlas...\n")
usuarios = list(db.usuarios.find({}).sort("nome", 1))

print(f"📊 Total de usuários encontrados: {len(usuarios)}\n")
print("=" * 80)

for i, user in enumerate(usuarios, 1):
    print(f"{i}. {user.get('nome')}")
    print(f"   Email: {user.get('email')}")
    print(f"   Tipo: {user.get('tipo')}")
    print(f"   Ativo: {user.get('ativo')}")
    print(f"   ID: {user.get('id')}")
    print()

# Verificar especificamente as três novas usuárias
print("=" * 80)
print("\n🔍 Verificando as três novas usuárias:\n")
print("\n🔎 Análise automática dos usuários:\n")
# Verificar duplicidade de emails
emails = [user.get('email') for user in usuarios if user.get('email')]
duplicados = set([email for email in emails if emails.count(email) > 1])
if duplicados:
    print(f"❗ Emails duplicados encontrados: {', '.join(duplicados)}")
else:
    print("✅ Nenhum email duplicado.")

# Verificar usuários inativos
inativos = [user for user in usuarios if not user.get('ativo', True)]
if inativos:
    print(f"❗ Usuários inativos: {len(inativos)}")
    for user in inativos:
        print(f"   {user.get('nome')} - {user.get('email')}")
else:
    print("✅ Todos os usuários estão ativos.")

# Verificar campos inconsistentes
inconsistentes = [user for user in usuarios if not user.get('nome') or not user.get('email') or not user.get('id')]
if inconsistentes:
    print(f"❗ Usuários com campos faltando: {len(inconsistentes)}")
    for user in inconsistentes:
        print(f"   {user.get('nome', 'N/A')} - {user.get('email', 'N/A')} - ID: {user.get('id', 'N/A')}")
else:
    print("✅ Todos os usuários possuem nome, email e ID.")

emails_novas = [
    "fabiana.coelho@ios.org.br",
    "juliete.pereira@ios.org.br", 
    "luana.soares@ios.org.br"
]

for email in emails_novas:
    usuario = db.usuarios.find_one({"email": email})
    if usuario:
        print(f"✅ ENCONTRADA: {usuario.get('nome')} ({email})")
        print(f"   Tipo: {usuario.get('tipo')}")
        print(f"   Ativo: {usuario.get('ativo')}")
        print(f"   ID: {usuario.get('id')}")
    else:
        print(f"❌ NÃO ENCONTRADA: {email}")
    print()

client.close()
