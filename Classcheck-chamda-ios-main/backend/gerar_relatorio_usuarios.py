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

# Buscar unidades e cursos para referência
unidades = {u['id']: u['nome'] for u in db.unidades.find({})}
cursos = {c['id']: c['nome'] for c in db.cursos.find({})}

print("=" * 150)
print(f"{'NOME':<35} {'EMAIL':<40} {'TIPO':<20} {'UNIDADE':<25} {'CURSO':<30}")
print("=" * 150)

dados_usuarios = []

for user in usuarios:
    nome = user.get('nome', '')
    email = user.get('email', '')
    tipo = user.get('tipo', '')
    unidade_id = user.get('unidade_id')
    curso_id = user.get('curso_id')
    
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
    
    # Para senhas, só vamos mostrar se são senhas temporárias conhecidas
    # As senhas estão em hash bcrypt, então não podemos recuperá-las
    senha_info = "Senha hash (redefinir via sistema)"
    
    # Verificar se tem senha temporária comum
    senha_hash = user.get('senha_hash') or user.get('senha', '')
    if senha_hash:
        # Testar senhas temporárias comuns
        senhas_teste = ['IOS@2026', 'admin123', 'b99018cd', '123456']
        for senha_temp in senhas_teste:
            try:
                if bcrypt.verify(senha_temp, senha_hash):
                    senha_info = f"🔑 {senha_temp}"
                    break
            except:
                pass
    
    print(f"{nome:<35} {email:<40} {tipo_label:<20} {unidade_nome:<25} {curso_nome:<30}")
    
    dados_usuarios.append({
        'nome': nome,
        'email': email,
        'tipo': tipo_label,
        'unidade': unidade_nome,
        'curso': curso_nome,
        'senha': senha_info
    })

print("=" * 150)
print(f"\n📊 Total de usuários: {len(usuarios)}\n")

# Gerar arquivo CSV
import csv

with open('usuarios_completo.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
    fieldnames = ['Nome', 'Email', 'Tipo', 'Unidade', 'Curso', 'Senha']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    writer.writeheader()
    for user in dados_usuarios:
        writer.writerow({
            'Nome': user['nome'],
            'Email': user['email'],
            'Tipo': user['tipo'],
            'Unidade': user['unidade'],
            'Curso': user['curso'],
            'Senha': user['senha']
        })

print("💾 Arquivo gerado: usuarios_completo.csv")

print("\n" + "=" * 150)
print("📋 RESUMO POR TIPO:")
print("=" * 150)

from collections import Counter
tipos_count = Counter([u['tipo'] for u in dados_usuarios])
for tipo, count in sorted(tipos_count.items()):
    print(f"  {tipo:<30} {count:>3} usuários")

print("\n" + "=" * 150)
print("🔐 INFORMAÇÕES DE ACESSO - SENHAS CONHECIDAS:")
print("=" * 150)

for user in dados_usuarios:
    if '🔑' in user['senha']:
        print(f"  {user['nome']:<35} {user['email']:<40} {user['senha']}")

print("\n⚠️  NOTA: Senhas em hash bcrypt não podem ser recuperadas.")
print("   Use a função 'Redefinir Senha' no sistema para gerar novas senhas temporárias.")

client.close()
