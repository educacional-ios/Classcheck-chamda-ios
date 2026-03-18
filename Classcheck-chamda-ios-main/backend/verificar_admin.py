import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME")

async def verificar_admin():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("\n🔍 Buscando usuário admin...\n")
    
    # Buscar admin
    admin = await db.usuarios.find_one({"tipo": "admin"})
    
    if admin:
        print(f"👤 Admin encontrado:")
        print(f"   Nome: {admin.get('nome')}")
        print(f"   Email: {admin.get('email')}")
        print(f"   ID: {admin.get('id')}")
        print(f"   Tipo: {admin.get('tipo')}")
    else:
        print("❌ Nenhum admin encontrado!")
        print("\nUsuários disponíveis:")
        usuarios = await db.usuarios.find().to_list(10)
        for u in usuarios:
            print(f"   - {u.get('nome')} ({u.get('email')}) - Tipo: {u.get('tipo')}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(verificar_admin())
