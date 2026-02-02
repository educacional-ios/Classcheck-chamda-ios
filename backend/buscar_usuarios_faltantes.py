import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME")

async def buscar_usuarios():
    print(f"\n🔌 Conectando ao MongoDB Atlas (Produção)...")
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    await client.admin.command('ping')
    print("✅ Conectado!\n")
    
    # Buscar usuários que possam ser Dayane ou Amanda
    print("🔍 Buscando usuários com 'dayane', 'amanda', 'rocha' ou 'ferreira'...\n")
    
    query = {
        "$or": [
            {"nome": {"$regex": "dayane", "$options": "i"}},
            {"nome": {"$regex": "amanda", "$options": "i"}},
            {"nome": {"$regex": "rocha", "$options": "i"}},
            {"nome": {"$regex": "ferreira", "$options": "i"}},
            {"email": {"$regex": "dayane", "$options": "i"}},
            {"email": {"$regex": "amanda", "$options": "i"}},
        ]
    }
    
    usuarios_encontrados = await db.usuarios.find(query).to_list(None)
    
    if usuarios_encontrados:
        print("✅ Usuários encontrados:")
        for user in usuarios_encontrados:
            print(f"\n   Nome: {user.get('nome')}")
            print(f"   Email: {user.get('email')}")
            print(f"   Tipo: {user.get('tipo')}")
            print(f"   ID: {user.get('id')}")
    else:
        print("❌ Nenhum usuário com esses nomes foi encontrado.")
        print("\n📋 Listando TODOS os usuários do banco (total):")
        
        todos = await db.usuarios.find().sort("nome", 1).to_list(None)
        print(f"\nTotal: {len(todos)} usuários\n")
        
        for i, user in enumerate(todos, 1):
            print(f"{i}. {user.get('nome')} - {user.get('email')} - {user.get('tipo')}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(buscar_usuarios())
