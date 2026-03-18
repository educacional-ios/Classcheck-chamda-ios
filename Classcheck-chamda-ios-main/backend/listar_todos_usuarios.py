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

async def listar_todos():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    await client.admin.command('ping')
    print("✅ Conectado ao MongoDB Atlas - Produção\n")
    
    # Buscar TODOS os usuários sem limite
    cursor = db.usuarios.find({})
    usuarios = await cursor.to_list(length=None)
    
    print(f"📊 Total de usuários no banco: {len(usuarios)}\n")
    print("=" * 140)
    print(f"{'#':<4} {'Nome':<40} {'Email':<45} {'Tipo':<25} {'Senha':<15}")
    print("=" * 140)
    
    usuarios_ordenados = sorted(usuarios, key=lambda x: x.get('nome', ''))
    
    for i, user in enumerate(usuarios_ordenados, 1):
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
        
        print(f"{i:<4} {nome:<40} {email:<45} {tipo_exibir:<25} {senha_padrao:<15}")
    
    print("=" * 140)
    print(f"\n✅ Listagem completa de {len(usuarios)} usuários\n")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(listar_todos())
