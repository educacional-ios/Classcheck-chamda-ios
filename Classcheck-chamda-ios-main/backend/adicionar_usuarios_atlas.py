from pymongo import MongoClient
from urllib.parse import quote_plus
from passlib.hash import bcrypt
import uuid
from datetime import datetime, timezone

# Conexão MongoDB Atlas
username = quote_plus("educacional_db_user")
password = quote_plus("qpvR7mlOHSoxwvQ8")

MONGO_URL = f"mongodb+srv://{username}:{password}@chamada-prod.nr10evs.mongodb.net/IOS-SISTEMA-CHAMADA?retryWrites=true&w=majority&appName=chamada-prod"
DB_NAME = "IOS-SISTEMA-CHAMADA"

print("🔌 Conectando ao MongoDB Atlas...")
client = MongoClient(MONGO_URL)
db = client[DB_NAME]

# Verificar conexão
try:
    client.admin.command('ping')
    print("✅ Conectado ao MongoDB Atlas com sucesso!\n")
except Exception as e:
    print(f"❌ Erro ao conectar: {e}")
    exit(1)

# Buscar unidades e cursos
print("🏢 Buscando unidades...")
unidades = list(db.unidades.find({"ativo": True}))
if not unidades:
    print("❌ Nenhuma unidade encontrada!")
    exit(1)

print(f"✅ Encontradas {len(unidades)} unidades")
for i, unidade in enumerate(unidades[:5], 1):
    print(f"   {i}. {unidade.get('nome')}")

unidade_padrao = unidades[0]['id']
print(f"\n📍 Usando unidade: {unidades[0].get('nome')}\n")

print("📚 Buscando cursos...")
cursos = list(db.cursos.find({"ativo": True}))
if not cursos:
    print("❌ Nenhum curso encontrado!")
    exit(1)

print(f"✅ Encontrados {len(cursos)} cursos")
for i, curso in enumerate(cursos[:5], 1):
    print(f"   {i}. {curso.get('nome')}")

curso_padrao = cursos[0]['id']
print(f"\n📖 Usando curso: {cursos[0].get('nome')}\n")

# Usuárias a serem adicionadas
usuarios_para_adicionar = [
    {
        "id": str(uuid.uuid4()),
        "nome": "Fabiana Pinto Coelho",
        "email": "fabiana.coelho@ios.org.br",
        "tipo": "instrutor",
        "telefone": "",
        "unidade_id": unidade_padrao,
        "curso_id": curso_padrao,
        "ativo": True,
        "primeiro_acesso": True,
        "senha_hash": bcrypt.hash("IOS@2026"),  # Senha temporária
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    },
    {
        "id": str(uuid.uuid4()),
        "nome": "Juliete Pereira",
        "email": "juliete.pereira@ios.org.br",
        "tipo": "pedagogo",
        "telefone": "",
        "unidade_id": unidade_padrao,
        "curso_id": curso_padrao,
        "ativo": True,
        "primeiro_acesso": True,
        "senha_hash": bcrypt.hash("IOS@2026"),  # Senha temporária
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    },
    {
        "id": str(uuid.uuid4()),
        "nome": "Luana Cristina Soares",
        "email": "luana.soares@ios.org.br",
        "tipo": "pedagogo",
        "telefone": "",
        "unidade_id": unidade_padrao,
        "curso_id": curso_padrao,
        "ativo": True,
        "primeiro_acesso": True,
        "senha_hash": bcrypt.hash("IOS@2026"),  # Senha temporária
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
]

print("👥 Adicionando usuárias ao MongoDB Atlas...\n")

for usuario in usuarios_para_adicionar:
    # Verificar se já existe
    existe = db.usuarios.find_one({"email": usuario['email']})
    
    if existe:
        print(f"⚠️  {usuario['nome']} ({usuario['email']}) já existe no sistema")
        print(f"   ID existente: {existe.get('id')}\n")
    else:
        # Inserir novo usuário
        resultado = db.usuarios.insert_one(usuario)
        print(f"✅ {usuario['nome']} adicionada com sucesso!")
        print(f"   Email: {usuario['email']}")
        print(f"   Tipo: {usuario['tipo']}")
        print(f"   ID: {usuario['id']}")
        print(f"   🔑 Senha temporária: IOS@2026")
        print()

print("\n📊 Verificando total de usuários no sistema...")
total_usuarios = db.usuarios.count_documents({})
print(f"Total de usuários: {total_usuarios}\n")

# Listar as usuárias adicionadas
emails = [u['email'] for u in usuarios_para_adicionar]
usuarios_encontrados = list(db.usuarios.find({"email": {"$in": emails}}))

if usuarios_encontrados:
    print("✅ Usuárias encontradas no MongoDB Atlas:")
    for user in usuarios_encontrados:
        print(f"   • {user.get('nome')} ({user.get('email')}) - {user.get('tipo')}")
else:
    print("⚠️ Nenhuma usuária encontrada")

print("\n✅ Processo concluído!")
client.close()
