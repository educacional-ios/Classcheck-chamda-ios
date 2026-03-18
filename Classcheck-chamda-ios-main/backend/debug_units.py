import os
from pymongo import MongoClient
import certifi

# --- CONFIG ---
MONGO_URI = "mongodb+srv://educacional_db_user:qpvR7mlOHSoxwvQ8@chamada-prod.nr10evs.mongodb.net/IOS-SISTEMA-CHAMADA?retryWrites=true&w=majority&appName=chamada-prod"
DB_NAME = "IOS-SISTEMA-CHAMADA"

def main():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    
    print(f"Total Turmas: {db.turmas.count_documents({})}")
    print("\n--- FIRST TURMA ---")
    print(db.turmas.find_one())

    print("\n--- SAMPLE BARREIRO ---")
    sample = db.turmas.find_one({"unidade": "Barreiro"})
    print(sample)
    
    print("\n--- SAMPLE HORTOLANDIA ---")
    sample2 = db.turmas.find_one({"unidade": {"$regex": "Horto", "$options": "i"}})
    if sample2:
        print(f"Unidade: {sample2.get('unidade')} | Ativa: {sample2.get('ativa')}")
    else:
        print("None found")

if __name__ == "__main__":
    main()
