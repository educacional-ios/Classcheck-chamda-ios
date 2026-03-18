import requests
from pymongo import MongoClient
from datetime import datetime
import uuid

API_URL = "https://sistema-ios-backend.onrender.com"

# IDs dos instrutores
IAGO_ID = "03dea76b-9932-4240-982b-bf406bb3f003"
RAISSA_ID = "41082b8d-4359-4fdd-a5e2-98c54871bf31"

print("\n" + "="*80)
print("🎯 DESCOBRINDO O BANCO E CRIANDO TURMA DEMO")
print("="*80)

# 1. Login
print("\n1️⃣ Fazendo login...")
login = requests.post(
    f"{API_URL}/api/auth/login",
    json={"email": "jesiel.junior@ios.org.br", "senha": "b99018cd"}
)
token = login.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 2. Buscar uma turma qualquer pra pegar o padrão
print("\n2️⃣ Buscando turmas pra entender o padrão...")
turmas = requests.get(f"{API_URL}/api/classes", headers=headers).json()
print(f"   Total: {len(turmas)} turmas")

turma_exemplo = turmas[0]
print(f"\n   Exemplo de turma:")
print(f"   Nome: {turma_exemplo.get('nome')}")
print(f"   ID: {turma_exemplo.get('id')}")

# 3. Pegar IDs de curso e unidade de uma turma existente
curso_id = turma_exemplo.get('curso_id')
unidade_id = turma_exemplo.get('unidade_id')

print(f"   curso_id: {curso_id}")
print(f"   unidade_id: {unidade_id}")

# 4. Criar turma DEMO via API
print("\n4️⃣ Criando turma DEMO com 2 instrutores via API...")

nova_turma = {
    "nome": "DEMO 2 INSTRUTORES - NÃO MEXER",
    "instrutor_id": IAGO_ID,  # Requerido pelo backend antigo
    "instrutor_ids": [IAGO_ID, RAISSA_ID],  # Novo formato
    "curso_id": curso_id,
    "unidade_id": unidade_id,
    "turno": "Manhã",
    "data_inicio": "2026-02-01",
    "data_fim": "2026-12-31",
    "horario_inicio": "08:00",
    "horario_fim": "12:00",
    "dias_semana": ["segunda", "quarta", "sexta"],
    "ativo": True
}

response = requests.post(
    f"{API_URL}/api/classes",
    headers=headers,
    json=nova_turma
)

print(f"   Status: {response.status_code}")

if response.status_code in [200, 201]:
    turma_criada = response.json()
    print(f"   🎉 TURMA CRIADA!")
    print(f"   ID: {turma_criada.get('id')}")
    print(f"   instrutor_ids: {turma_criada.get('instrutor_ids')}")
    
    print(f"\n✅ TESTE AGORA:")
    print(f"   Login Raissa: raissa.pinho@ios.org.br / b99018cd")
    print(f"   Login Iago: iago.herbert@ios.org.br / b99018cd")
    print(f"   Ambos devem ver a turma DEMO!")
else:
    print(f"   ❌ Erro: {response.text}")

print("\n" + "="*80)
