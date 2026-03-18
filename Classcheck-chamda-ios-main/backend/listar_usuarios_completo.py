import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME")

def gerar_senha_temporaria(nome_completo: str) -> str:
    """
    Gera senha temporária no padrão: IOS2026 + iniciais do nome
    """
    palavras = nome_completo.strip().split()
    iniciais = ''.join([p[0].lower() for p in palavras if p])
    iniciais = iniciais[:5]
    return f"IOS2026{iniciais}"

async def listar_usuarios():
    print(f"\n🔌 Conectando ao MongoDB Atlas...")
    print(f"📍 URL: {MONGO_URL[:50]}...")
    print(f"🗄️  Database: {DB_NAME}\n")
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Testar conexão
    await client.admin.command('ping')
    print("✅ Conectado ao MongoDB Atlas!\n")
    
    print("🔍 Buscando todos os usuários...\n")
    print("=" * 150)
    print(f"{'Nome':<40} {'Email':<45} {'Tipo':<25} {'Senha Padrão':<20}")
    print("=" * 150)
    
    # Buscar todos os usuários
    usuarios = await db.usuarios.find().sort("nome", 1).to_list(None)
    
    for user in usuarios:
        nome = user.get('nome', 'N/A')
        email = user.get('email', 'N/A')
        tipo = user.get('tipo', 'N/A')
        
        # Gerar senha no padrão
        senha_padrao = gerar_senha_temporaria(nome)
        
        # Traduzir tipo de usuário
        tipo_map = {
            'admin': 'Administrador(a)',
            'instrutor': 'Professor(a)',
            'pedagogo': 'Coord. Pedagógico',
            'monitor': 'Monitor(a)'
        }
        tipo_exibir = tipo_map.get(tipo, tipo)
        
        print(f"{nome:<40} {email:<45} {tipo_exibir:<25} {senha_padrao:<20}")
    
    print("=" * 150)
    print(f"\n📊 Total de usuários encontrados: {len(usuarios)}\n")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(listar_usuarios())
