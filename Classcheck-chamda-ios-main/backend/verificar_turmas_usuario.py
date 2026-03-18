from pymongo import MongoClient
from urllib.parse import quote_plus
import sys

# Conexão MongoDB Atlas
username = quote_plus("educacional_db_user")
password = quote_plus("qpvR7mlOHSoxwvQ8")
MONGO_URL = f"mongodb+srv://{username}:{password}@chamada-prod.nr10evs.mongodb.net/IOS-SISTEMA-CHAMADA?retryWrites=true&w=majority&appName=chamada-prod"
DB_NAME = "IOS-SISTEMA-CHAMADA"

client = MongoClient(MONGO_URL)
db = client[DB_NAME]

def verificar():
    turmas_nomes = [
        "Gestão Empresarial ERP - Barreiro BH Manhã T1",
        "Gestão Empresarial ERP - Barreiro BH Manhã T2",
        "Gestão Empresarial ERP - Barreiro BH Tarde T3",
        "Gestão Empresarial ERP - Barreiro BH Tarde T4",
        "Suporte TI - Hortolândia Manhã T1",
        "Suporte TI - Hortolândia Tarde T2"
    ]

    print("=" * 100)
    print("VERIFICAÇÃO DE INSTRUTORES POR TURMA")
    print("=" * 100)

    # Cache de usuarios para não consultar o banco toda hora
    usuarios_cache = {}

    for nome_turma in turmas_nomes:
        # Busca flexível por nome
        turma = db.turmas.find_one({"nome": {"$regex": nome_turma, "$options": "i"}})
        
        if not turma:
            print(f"❌ Turma NÃO encontrada: {nome_turma}")
            continue

        print(f"\n📚 Turma: {turma.get('nome')}")
        instrutor_ids = turma.get('instrutor_ids', [])
        
        # Fallback para campo antigo se vazio
        if not instrutor_ids and turma.get('instrutor_id'):
            instrutor_ids = [turma.get('instrutor_id')]
            print("   ⚠️  Usando campo antigo 'instrutor_id'")

        count = len(instrutor_ids)
        if count == 0:
            print("   ❌ NENHUM instrutor vinculado!")
        elif count == 2:
            print(f"   ✅ {count} INSTRUTORES (Correto)")
        else:
            print(f"   ⚠️  {count} INSTRUTOR(ES)")

        # Listar nomes
        for i, uid in enumerate(instrutor_ids, 1):
            if uid not in usuarios_cache:
                u = db.usuarios.find_one({"id": uid})
                usuarios_cache[uid] = u.get('nome') if u else "DESCONHECIDO"
            
            print(f"      {i}. {usuarios_cache[uid]} (ID: {uid})")

if __name__ == "__main__":
    verificar()
