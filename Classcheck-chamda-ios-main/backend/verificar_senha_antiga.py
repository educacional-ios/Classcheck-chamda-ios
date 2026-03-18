import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
from passlib.hash import bcrypt

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME")

async def verificar_senha():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    await client.admin.command('ping')
    print("✅ Conectado ao MongoDB Atlas\n")
    
    # Buscar usuário Dayane
    dayane = await db.usuarios.find_one({"email": "dayane.rocha@ios.org.br"})
    
    if dayane:
        print("👤 Usuária: Dayane Silvestre da Rocha")
        print(f"📧 Email: {dayane.get('email')}")
        print(f"🔐 Hash da senha no banco: {dayane.get('senha')}\n")
        
        # Testar várias possibilidades de senha
        senhas_testar = [
            "IOS2026dsdr",  # Padrão novo
            "ios@2025",      # Padrão antigo comum
            "ios@2024",
            "ios@2026",
            "Ios@2025",
            "iOS@2025",
            "dayane.rocha",
            "123456",
            "admin",
            "ios123",
            "ios2025"
        ]
        
        print("🔍 Testando senhas...\n")
        senha_hash = dayane.get('senha')
        
        for senha in senhas_testar:
            try:
                if bcrypt.verify(senha, senha_hash):
                    print(f"✅ SENHA CORRETA ENCONTRADA: {senha}")
                    break
            except:
                pass
        else:
            print("❌ Nenhuma das senhas testadas funcionou")
            print("\nPreciso redefinir com um padrão diferente")
    
    await client.close()

asyncio.run(verificar_senha())
