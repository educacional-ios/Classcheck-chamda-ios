from pymongo import MongoClient
from urllib.parse import quote_plus

# Conexão MongoDB
username = quote_plus("educacional_db_user")
password = quote_plus("qpvR7mlOHSoxwvQ8")
MONGO_URL = f"mongodb+srv://{username}:{password}@chamada-prod.nr10evs.mongodb.net/IOS-SISTEMA-CHAMADA?retryWrites=true&w=majority&appName=chamada-prod"
DB_NAME = "IOS-SISTEMA-CHAMADA"

client = MongoClient(MONGO_URL)
db = client[DB_NAME]

def buscar_elizabeth():
    print("=" * 60)
    print("Listing ALL users...")
    cursor = db.usuarios.find({})
    count = 0
    for u in cursor:
        print(f"User: {u.get('nome', 'N/A')} | ID: {u.get('id', 'N/A')} | Role: {u.get('tipo', 'N/A')}")
        count += 1
        if count > 2000: break

if __name__ == "__main__":
    buscar_elizabeth()
