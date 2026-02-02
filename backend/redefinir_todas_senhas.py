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

def gerar_senha_temporaria(nome_completo: str) -> str:
    """
    Gera senha temporária no padrão: IOS2026 + iniciais do nome
    """
    palavras = nome_completo.strip().split()
    iniciais = ''.join([p[0].lower() for p in palavras if p])
    iniciais = iniciais[:5]
    return f"IOS2026{iniciais}"

print("🔌 Conectando ao MongoDB Atlas...")
client.admin.command('ping')
print("✅ Conectado!\n")

# Buscar todos os usuários
usuarios = list(db.usuarios.find({}).sort("nome", 1))

# Buscar unidades e cursos para referência
unidades = {u['id']: u['nome'] for u in db.unidades.find({})}
cursos = {c['id']: c['nome'] for c in db.cursos.find({})}

print("🔐 REDEFININDO SENHAS PARA O NOVO PADRÃO...\n")
print("=" * 130)

dados_usuarios = []

for user in usuarios:
    nome = user.get('nome', '')
    email = user.get('email', '')
    tipo = user.get('tipo', '')
    user_id = user.get('id')
    unidade_id = user.get('unidade_id')
    curso_id = user.get('curso_id')
    
    # Gerar nova senha no padrão
    nova_senha = gerar_senha_temporaria(nome)
    senha_hash = bcrypt.hash(nova_senha)
    
    # Atualizar no banco
    db.usuarios.update_one(
        {"id": user_id},
        {"$set": {
            "senha": senha_hash,
            "primeiro_acesso": True
        }}
    )
    
    # Traduzir tipo
    tipo_label = {
        'admin': 'Administrador(a)',
        'instrutor': 'Professor(a)',
        'pedagogo': 'Coordenação Pedagógica',
        'monitor': 'Monitor(a)'
    }.get(tipo, tipo)
    
    # Buscar nomes de unidade e curso
    unidade_nome = unidades.get(unidade_id, '-') if unidade_id else '-'
    curso_nome = cursos.get(curso_id, '-') if curso_id else '-'
    
    dados_usuarios.append({
        'nome': nome,
        'email': email,
        'senha': nova_senha,
        'tipo': tipo_label,
        'unidade': unidade_nome,
        'curso': curso_nome
    })
    
    print(f"✅ {nome:<35} → {nova_senha}")

print("=" * 130)
print(f"\n📊 Total de usuários atualizados: {len(usuarios)}\n")

# Gerar tabela formatada
print("\n" + "=" * 130)
print("📋 TABELA COMPLETA DE USUÁRIOS E SENHAS")
print("=" * 130)
print(f"{'NOME':<35} {'EMAIL':<40} {'SENHA':<15} {'TIPO':<25}")
print("=" * 130)

for user in dados_usuarios:
    print(f"{user['nome']:<35} {user['email']:<40} {user['senha']:<15} {user['tipo']:<25}")

print("=" * 130)

# Gerar CSV
import csv

with open('usuarios_senhas_atualizadas.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
    fieldnames = ['Nome', 'Email', 'Senha', 'Tipo', 'Unidade', 'Curso']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    writer.writeheader()
    for user in dados_usuarios:
        writer.writerow({
            'Nome': user['nome'],
            'Email': user['email'],
            'Senha': user['senha'],
            'Tipo': user['tipo'],
            'Unidade': user['unidade'],
            'Curso': user['curso']
        })

print("\n💾 Arquivo CSV gerado: usuarios_senhas_atualizadas.csv")

# Resumo por tipo
from collections import Counter
print("\n" + "=" * 130)
print("📊 RESUMO POR TIPO:")
print("=" * 130)

tipos_count = Counter([u['tipo'] for u in dados_usuarios])
for tipo, count in sorted(tipos_count.items()):
    print(f"  {tipo:<30} {count:>3} usuários")

print("\n" + "=" * 130)
print("✅ TODAS AS SENHAS FORAM REDEFINIDAS PARA O PADRÃO: IOS2026 + INICIAIS")
print("=" * 130)

client.close()
