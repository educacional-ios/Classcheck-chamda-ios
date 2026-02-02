import requests
import json

API_URL = "https://sistema-ios-backend.onrender.com/api"

print("🔐 Fazendo login...")
login_response = requests.post(f"{API_URL}/auth/login", json={
    "email": "jesiel.junior@ios.org.br",
    "senha": "b99018cd"
})

if login_response.status_code != 200:
    print(f"❌ Login falhou: {login_response.text}")
    exit(1)

token = login_response.json()['access_token']
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

print("✅ Login OK\n")

# Buscar unidades
unidades_response = requests.get(f"{API_URL}/units", headers=headers)
unidades = unidades_response.json()
unidade_id = unidades[0]['id']
print(f"📍 Unidade: {unidades[0]['nome']}\n")

# Buscar cursos
cursos_response = requests.get(f"{API_URL}/courses", headers=headers)
cursos = cursos_response.json()
curso_id = cursos[0]['id']
print(f"📖 Curso: {cursos[0]['nome']}\n")

usuarios = [
    {
        "nome": "Fabiana Pinto Coelho",
        "email": "fabiana.coelho@ios.org.br",
        "tipo": "instrutor",
        "telefone": "",
        "unidade_id": unidade_id,
        "curso_id": curso_id
    },
    {
        "nome": "Juliete Pereira",
        "email": "juliete.pereira@ios.org.br",
        "tipo": "pedagogo",
        "telefone": "",
        "unidade_id": unidade_id,
        "curso_id": curso_id
    },
    {
        "nome": "Luana Cristina Soares",
        "email": "luana.soares@ios.org.br",
        "tipo": "pedagogo",
        "telefone": "",
        "unidade_id": unidade_id,
        "curso_id": curso_id
    }
]

print("👥 Criando usuárias via API...\n")

for user in usuarios:
    print(f"Criando: {user['nome']}...")
    response = requests.post(f"{API_URL}/users", headers=headers, json=user)
    
    if response.status_code in [200, 201]:
        print(f"✅ Criada com sucesso!")
        data = response.json()
        if 'senha_temporaria' in data:
            print(f"   🔑 Senha: {data['senha_temporaria']}")
    else:
        print(f"❌ Erro: {response.status_code} - {response.text}")
    print()

print("\n🔍 Verificando se aparecem na lista...\n")
users_response = requests.get(f"{API_URL}/users", headers=headers)
usuarios_api = users_response.json()

print(f"Total na API: {len(usuarios_api)}\n")

for email in ["fabiana.coelho@ios.org.br", "juliete.pereira@ios.org.br", "luana.soares@ios.org.br"]:
    encontrado = next((u for u in usuarios_api if u['email'] == email), None)
    if encontrado:
        print(f"✅ {encontrado['nome']}")
    else:
        print(f"❌ {email} NÃO ENCONTRADO")
