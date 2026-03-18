import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
import bcrypt

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME")

async def reset_admin_password():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Buscar admin
    admin = await db.usuarios.find_one({"tipo": "admin"})
    
    if admin:
        # Resetar senha para "admin123"
        nova_senha = "admin123"
        senha_hash = bcrypt.hashpw(nova_senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        await db.usuarios.update_one(
            {"id": admin['id']},
            {"$set": {"senha": senha_hash}}
        )
        
        print(f"✅ Senha do admin resetada para: {nova_senha}")
        print(f"   Email: {admin['email']}")
    else:
        print("❌ Admin não encontrado")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(reset_admin_password())
