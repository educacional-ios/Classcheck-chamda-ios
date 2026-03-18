import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME")

async def buscar_dayane_amanda():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("🔍 Buscando Dayane e Amanda especificamente...\n")
    
    # Buscar por emails exatos
    usuarios = await db.usuarios.find({
        "$or": [
            {"email": "dayane.rocha@ios.org.br"},
            {"email": "amanda.santos@ios.org.br"}
        ]
    }).to_list(10)
    
    print(f"Encontrados: {len(usuarios)}\n")
    
    if usuarios:
        for u in usuarios:
            print(f"Nome: {u.get('nome')}")
            print(f"Email: {u.get('email')}")
            print(f"Tipo: {u.get('tipo')}")
            print(f"ID: {u.get('id')}")
            
            # Gerar senha
            nome = u.get('nome', '')
            palavras = nome.strip().split()
            iniciais = ''.join([p[0].lower() for p in palavras if p])[:5]
            senha = f"IOS2026{iniciais}"
            print(f"Senha: {senha}")
            print("-" * 50)
    else:
        print("❌ NÃO ENCONTRADO no banco!")
        print("\nVerificando se o frontend está usando outra URL de API...")
    
    await client.close()

asyncio.run(buscar_dayane_amanda())
