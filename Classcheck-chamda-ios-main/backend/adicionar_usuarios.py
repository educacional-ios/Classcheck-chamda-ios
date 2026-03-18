import requests
import json

# 🌐 API URL - PRODUÇÃO (Render)
API_URL = "https://sistema-ios-backend.onrender.com/api"

# Credenciais de admin
login_data = {
    "email": "admin@ios.com.br",
    "senha": "admin123"
}

# Usuárias a serem adicionadas
usuarios_para_adicionar = [
    {
        "nome": "Fabiana Pinto Coelho",
        "email": "fabiana.coelho@ios.org.br",
        "tipo": "instrutor",
        "telefone": "",
        "unidade_id": None,
        "curso_id": None
    },
    {
        "nome": "Juliete Pereira",
        "email": "juliete.pereira@ios.org.br",
        "tipo": "pedagogo",
        "telefone": "",
        "unidade_id": None,
        "curso_id": None
    },
    {
        "nome": "Luana Cristina Soares",
        "email": "luana.soares@ios.org.br",
        "tipo": "pedagogo",
        "telefone": "",
        "unidade_id": None,
        "curso_id": None
    }
]

try:
    print("\n🔐 Fazendo login como admin...")
    login_response = requests.post(f"{API_URL}/auth/login", json=login_data)
    
    if login_response.status_code == 200:
        token_data = login_response.json()
        token = token_data.get('access_token')
        print(f"✅ Login bem-sucedido!")
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        # Buscar unidades disponíveis
        print("\n🏢 Buscando unidades disponíveis...")
        unidades_response = requests.get(f"{API_URL}/units", headers=headers)
        
        if unidades_response.status_code == 200:
            unidades = unidades_response.json()
            print(f"✅ Encontradas {len(unidades)} unidades\n")
            
            for i, unidade in enumerate(unidades, 1):
                print(f"{i}. {unidade.get('nome')} - ID: {unidade.get('id')}")
            
            if not unidades:
                print("\n❌ Nenhuma unidade encontrada! Por favor, crie uma unidade primeiro.")
                exit(1)
            
            # Usar a primeira unidade disponível como padrão
            unidade_padrao = unidades[0]['id']
            print(f"\n📍 Usando unidade padrão: {unidades[0].get('nome')}")
        else:
            print(f"❌ Erro ao buscar unidades: {unidades_response.status_code}")
            print(f"Resposta: {unidades_response.text}")
            exit(1)
        
        # Buscar cursos disponíveis
        print("\n📚 Buscando cursos disponíveis...")
        cursos_response = requests.get(f"{API_URL}/courses", headers=headers)
        
        if cursos_response.status_code == 200:
            cursos = cursos_response.json()
            print(f"✅ Encontrados {len(cursos)} cursos\n")
            
            for i, curso in enumerate(cursos[:5], 1):
                print(f"{i}. {curso.get('nome')} - ID: {curso.get('id')}")
            
            if not cursos:
                print("\n❌ Nenhum curso encontrado! Por favor, crie um curso primeiro.")
                exit(1)
            
            # Usar o primeiro curso disponível como padrão
            curso_padrao = cursos[0]['id']
            print(f"\n📖 Usando curso padrão: {cursos[0].get('nome')}")
            
            # Atualizar usuários com a unidade e curso
            for usuario in usuarios_para_adicionar:
                usuario['unidade_id'] = unidade_padrao
                usuario['curso_id'] = curso_padrao
        else:
            print(f"❌ Erro ao buscar cursos: {cursos_response.status_code}")
            print(f"Resposta: {cursos_response.text}")
            exit(1)
        
        print("\n👥 Adicionando usuárias ao sistema...\n")
        
        for usuario in usuarios_para_adicionar:
            print(f"📝 Criando usuária: {usuario['nome']}")
            print(f"   Email: {usuario['email']}")
            print(f"   Tipo: {usuario['tipo']}")
            
            # Criar usuário
            create_response = requests.post(
                f"{API_URL}/users",
                headers=headers,
                json=usuario
            )
            
            if create_response.status_code in [200, 201]:
                user_data = create_response.json()
                print(f"   ✅ Usuária criada com sucesso!")
                print(f"   ID: {user_data.get('id')}")
                if 'senha_temporaria' in user_data:
                    print(f"   🔑 Senha temporária: {user_data.get('senha_temporaria')}")
                print()
            else:
                print(f"   ❌ Erro ao criar usuária: {create_response.status_code}")
                print(f"   Resposta: {create_response.text}")
                print()
        
        # Listar todos os usuários para confirmar
        print("\n📋 Verificando usuários criados...\n")
        users_response = requests.get(f"{API_URL}/users", headers=headers)
        
        if users_response.status_code == 200:
            users = users_response.json()
            print(f"Total de usuários no sistema: {len(users)}\n")
            
            # Filtrar as usuárias recém-criadas
            emails_adicionados = [u['email'] for u in usuarios_para_adicionar]
            usuarios_criados = [u for u in users if u.get('email') in emails_adicionados]
            
            if usuarios_criados:
                print("✅ Usuárias adicionadas encontradas no sistema:")
                for user in usuarios_criados:
                    print(f"   • {user.get('nome')} ({user.get('email')}) - {user.get('tipo')}")
            else:
                print("⚠️ Nenhuma das usuárias adicionadas foi encontrada na listagem")
        
    else:
        print(f"\n❌ Erro no login: {login_response.status_code}")
        print(f"Resposta: {login_response.text}")
        
except Exception as e:
    print(f"\n❌ Erro: {e}")
    import traceback
    traceback.print_exc()
    print("\n⚠️ Certifique-se de que o backend está rodando em http://localhost:8000")
