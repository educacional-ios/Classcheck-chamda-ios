from pymongo import MongoClient
from urllib.parse import quote_plus
from passlib.hash import bcrypt
import uuid

# Conexão MongoDB Atlas
username = quote_plus("educacional_db_user")
password = quote_plus("qpvR7mlOHSoxwvQ8")

MONGO_URL = f"mongodb+srv://{username}:{password}@chamada-prod.nr10evs.mongodb.net/IOS-SISTEMA-CHAMADA?retryWrites=true&w=majority&appName=chamada-prod"
DB_NAME = "IOS-SISTEMA-CHAMADA"

client = MongoClient(MONGO_URL)
db = client[DB_NAME]

def gerar_senha_temporaria(nome_completo: str) -> str:
    """Gera senha temporária no padrão: IOS2026 + iniciais do nome"""
    palavras = nome_completo.strip().split()
    iniciais = ''.join([p[0].lower() for p in palavras if p])[:5]
    return f"IOS2026{iniciais}"

print("🔌 Conectando ao MongoDB Atlas...")
client.admin.command('ping')
print("✅ Conectado!\n")

# Dados das novas usuárias
novos_usuarios = [
    {
        "nome": "Dayane Silvestre da Rocha",
        "email": "dayane.rocha@ios.org.br",
        "tipo": "admin"
    },
    {
        "nome": "Amanda Ferreira Santos",
        "email": "amanda.santos@ios.org.br",
        "tipo": "admin"
    }
]

print("➕ Adicionando Dayane e Amanda ao banco...\n")
print("=" * 130)

for user_data in novos_usuarios:
    nome = user_data['nome']
    email = user_data['email']
    tipo = user_data['tipo']
    
    # Verificar se já existe
    existe = db.usuarios.find_one({"email": email})
    
    if existe:
        print(f"⚠️  {nome} já existe no banco!")
        continue
    
    # Gerar senha e hash
    senha_temporaria = gerar_senha_temporaria(nome)
    senha_hash = bcrypt.hash(senha_temporaria)
    
    # Criar usuário
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
    
    # Inserir no banco
    db.usuarios.insert_one(novo_usuario)
    
    print(f"✅ {nome:<40} | {email:<45} | Senha: {senha_temporaria}")

print("=" * 130)
print("\n✅ Usuárias adicionadas com sucesso!\n")

# Listar todos os usuários agora
print("📋 LISTA COMPLETA ATUALIZADA:\n")
todos_usuarios = list(db.usuarios.find({}).sort("nome", 1))

print(f"Total: {len(todos_usuarios)} usuários\n")
print("=" * 130)
print(f"{'Nome':<40} {'Email':<45} {'Tipo':<25} {'Senha':<15}")
print("=" * 130)

for user in todos_usuarios:
    nome = user.get('nome')
    email = user.get('email')
    tipo = user.get('tipo')
    
    # Gerar senha padrão
    senha_padrao = gerar_senha_temporaria(nome)
    
    tipo_map = {
        'admin': 'Administrador(a)',
        'instrutor': 'Professor(a)',
        'pedagogo': 'Coord. Pedagógico'
    }
    tipo_exibir = tipo_map.get(tipo, tipo)
    
    print(f"{nome:<40} {email:<45} {tipo_exibir:<25} {senha_padrao:<15}")

print("=" * 130)

client.close()
