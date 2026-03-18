from pymongo import MongoClient
from urllib.parse import quote_plus
from passlib.context import CryptContext

# MongoDB Atlas connection
username = quote_plus("educacional_db_user")
password = quote_plus("qpvR7mlOHSoxwvQ8")
MONGO_URI = f"mongodb+srv://{username}:{password}@chamada-prod.nr10evs.mongodb.net/IOS-SISTEMA-CHAMADA?retryWrites=true&w=majority&appName=chamada-prod"
DATABASE_NAME = "IOS-SISTEMA-CHAMADA"

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
users_collection = db["usuarios"]

# Passlib configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Usuário para testar
email_teste = "jesiel.junior@ios.org.br"
senha_teste = "IOS2026jj"

print(f"🔍 Verificando hash de senha para: {email_teste}\n")

# Buscar usuário no banco
user = users_collection.find_one({"email": email_teste})

if user:
    print(f"✅ Usuário encontrado:")
    print(f"   Nome: {user.get('nome')}")
    print(f"   Email: {user.get('email')}")
    print(f"   Hash armazenado: {user.get('senha')[:60]}...")
    
    # Testar verificação do hash
    print(f"\n🔐 Testando senha: '{senha_teste}'")
    
    senha_hash = user.get('senha')
    verifica = pwd_context.verify(senha_teste, senha_hash)
    
    print(f"   Resultado da verificação: {verifica}")
    
    if verifica:
        print(f"   ✅ SENHA CORRETA! Hash bcrypt está válido")
    else:
        print(f"   ❌ SENHA INCORRETA! Hash não corresponde")
        
        # Vamos gerar um novo hash e comparar
        print(f"\n🔧 Gerando novo hash para '{senha_teste}':")
        novo_hash = pwd_context.hash(senha_teste)
        print(f"   Novo hash: {novo_hash[:60]}...")
        
        # Verificar o novo hash
        print(f"\n   Testando novo hash:")
        verifica_novo = pwd_context.verify(senha_teste, novo_hash)
        print(f"   Resultado: {verifica_novo}")
        
else:
    print(f"❌ Usuário não encontrado no banco de dados")

client.close()
