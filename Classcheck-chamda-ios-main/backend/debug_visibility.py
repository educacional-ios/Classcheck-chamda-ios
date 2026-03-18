from pymongo import MongoClient
from urllib.parse import quote_plus

# Conexão MongoDB Atlas
username = quote_plus("educacional_db_user")
password = quote_plus("qpvR7mlOHSoxwvQ8")
MONGO_URL = f"mongodb+srv://{username}:{password}@chamada-prod.nr10evs.mongodb.net/IOS-SISTEMA-CHAMADA?retryWrites=true&w=majority&appName=chamada-prod"
DB_NAME = "IOS-SISTEMA-CHAMADA"

client = MongoClient(MONGO_URL)
db = client[DB_NAME]

def inspect_data():
    raissa_id = '41082b8d-4359-4fdd-a5e2-98c54871bf31'
    
    # Simulate EXACTLY what server.py does
    query = {"ativo": True}
    
    # Case 1: The OLD logic (hypothetically)
    # query["instrutor_ids"] = raissa_id
    # query["curso_id"] = ...
    
    # Case 2: The NEW logic
    query["$or"] = [
        {"instrutor_ids": raissa_id},
        {"instrutor_id": raissa_id}
    ]
    
    print("\n--- Simulating Server Query ---")
    print(f"Query: {query}")
    
    count = db.turmas.count_documents(query)
    print(f"Matches: {count}")

    if count > 0:
        turmas = db.turmas.find(query)
        for t in turmas:
            print(f"Found: {t.get('nome')}")

if __name__ == "__main__":
    inspect_data()
