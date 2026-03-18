import os
from pymongo import MongoClient
import certifi

# --- CONFIG ---
MONGO_URI = "mongodb+srv://educacional_db_user:qpvR7mlOHSoxwvQ8@chamada-prod.nr10evs.mongodb.net/IOS-SISTEMA-CHAMADA?retryWrites=true&w=majority&appName=chamada-prod"
DB_NAME = "IOS-SISTEMA-CHAMADA"

def main():
    db = MongoClient(MONGO_URI)[DB_NAME]
    
    print("--- MAPPING USED UNIT IDS ---")
    turma_distinct_units = db.turmas.distinct("unidade_id")
    
    for uid in turma_distinct_units:
        unit = db.unidades.find_one({"id": uid})
        name = unit['nome'] if unit else "UNKNOWN"
        print(f"ID: {uid} -> {name}")

if __name__ == "__main__":
    main()
