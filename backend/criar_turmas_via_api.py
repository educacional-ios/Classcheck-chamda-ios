import requests
import json
from datetime import datetime

API_URL = "https://sistema-ios-backend.onrender.com/api"

# Login
login_data = {
    "email": "jesiel.junior@ios.org.br",
    "senha": "b99018cd"
}

print("\n🔐 Fazendo login...")
login_response = requests.post(f"{API_URL}/auth/login", json=login_data, timeout=30)

if login_response.status_code != 200:
    print(f"❌ Erro no login: {login_response.text}")
    exit()

token = login_response.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

print("✅ Login OK!\n")

# Buscar unidades, cursos e instrutores
print("📍 Buscando dados...")
unidades = requests.get(f"{API_URL}/units", headers=headers, timeout=30).json()
cursos = requests.get(f"{API_URL}/courses", headers=headers, timeout=30).json()
usuarios = requests.get(f"{API_URL}/users", headers=headers, timeout=30).json()

# Encontrar IDs
itaquera = next((u for u in unidades if "Itaquera" in u.get('nome', '')), None)
santo_amaro = next((u for u in unidades if "Santo Amaro" in u.get('nome', '')), None)
porto_alegre = next((u for u in unidades if "Porto Alegre" in u.get('nome', '')), None)

erp_curso = next((c for c in cursos if "ERP" in c.get('nome', '') or "Gestão" in c.get('nome', '')), None)
prog_web = next((c for c in cursos if "Programação Web" in c.get('nome', '') and "Noite" not in c.get('nome', '')), None)

jose_marcos = next((u for u in usuarios if u.get('email') == 'jose.marcos@ios.org.br'), None)
graziela = next((u for u in usuarios if u.get('email') == 'graziela.santos@ios.org.br'), None)
lise = next((u for u in usuarios if u.get('email') == 'lise.chaves@ios.org.br'), None)
ermerson = next((u for u in usuarios if u.get('email') == 'ermerson.barros@ios.org.br'), None)
gabriel = next((u for u in usuarios if u.get('email') == 'gabriel.bezerra@ios.org.br'), None)

print(f"Itaquera: {'✅' if itaquera else '❌'}")
print(f"Santo Amaro: {'✅' if santo_amaro else '❌'}")
print(f"Porto Alegre: {'✅' if porto_alegre else '❌'}")
print(f"Curso ERP: {'✅' if erp_curso else '❌'}")
print(f"Programação Web: {'✅' if prog_web else '❌'}")
print(f"José Marcos: {'✅' if jose_marcos else '❌'}")
print(f"Graziela: {'✅' if graziela else '❌'}")
print(f"Lise: {'✅' if lise else '❌'}")
print(f"Ermerson: {'✅' if ermerson else '❌'}")
print(f"Gabriel: {'✅' if gabriel else '❌'}")

if not all([itaquera, santo_amaro, porto_alegre, erp_curso, prog_web, jose_marcos, graziela, lise, ermerson, gabriel]):
    print("\n❌ Dados faltando! Crie primeiro as unidades, cursos e instrutores no Render.")
    exit()

# CRIAR TURMAS via API
turmas_criar = []

# Itaquera - 4 turmas
for i in range(1, 3):
    turmas_criar.append({
        "nome": f"Gestão Empresarial ERP - Itaquera Manhã T{i}",
        "unidade_id": itaquera['id'],
        "curso_id": erp_curso['id'],
        "instrutor_id": jose_marcos['id'],
        "data_inicio": "2026-02-01",
        "data_fim": "2026-06-30",
        "horario_inicio": "08:30",
        "horario_fim": "11:30",
        "dias_semana": ["segunda", "terca", "quarta", "quinta"],
        "vagas_total": 20,
        "ciclo": "01/2026",
        "tipo_turma": "regular"
    })

for i in range(1, 3):
    turmas_criar.append({
        "nome": f"Gestão Empresarial ERP - Itaquera Tarde T{i}",
        "unidade_id": itaquera['id'],
        "curso_id": erp_curso['id'],
        "instrutor_id": jose_marcos['id'],
        "data_inicio": "2026-02-01",
        "data_fim": "2026-06-30",
        "horario_inicio": "14:00",
        "horario_fim": "17:00",
        "dias_semana": ["segunda", "terca", "quarta", "quinta"],
        "vagas_total": 20,
        "ciclo": "01/2026",
        "tipo_turma": "regular"
    })

# Santo Amaro - 2 turmas
turmas_criar.append({
    "nome": "Gestão Empresarial ERP - Santo Amaro Manhã",
    "unidade_id": santo_amaro['id'],
    "curso_id": erp_curso['id'],
    "instrutor_id": graziela['id'],
    "data_inicio": "2026-02-01",
    "data_fim": "2026-06-30",
    "horario_inicio": "08:00",
    "horario_fim": "12:00",
    "dias_semana": ["segunda", "terca", "quarta", "quinta", "sexta"],
    "vagas_total": 25,
    "ciclo": "01/2026",
    "tipo_turma": "regular"
})

turmas_criar.append({
    "nome": "Gestão Empresarial ERP - Santo Amaro Tarde",
    "unidade_id": santo_amaro['id'],
    "curso_id": erp_curso['id'],
    "instrutor_id": lise['id'],
    "data_inicio": "2026-02-01",
    "data_fim": "2026-06-30",
    "horario_inicio": "13:30",
    "horario_fim": "17:30",
    "dias_semana": ["segunda", "terca", "quarta", "quinta", "sexta"],
    "vagas_total": 25,
    "ciclo": "01/2026",
    "tipo_turma": "regular"
})

# Porto Alegre - 4 turmas
turmas_criar.extend([
    {
        "nome": "Programação Web Técnico - Porto Alegre Manhã",
        "unidade_id": porto_alegre['id'],
        "curso_id": prog_web['id'],
        "instrutor_id": ermerson['id'],
        "data_inicio": "2026-02-01",
        "data_fim": "2026-12-31",
        "horario_inicio": "08:00",
        "horario_fim": "12:00",
        "dias_semana": ["segunda", "terca", "quarta", "quinta", "sexta"],
        "vagas_total": 30,
        "ciclo": "01/2026",
        "tipo_turma": "regular"
    },
    {
        "nome": "Programação Web Técnico - Porto Alegre Tarde",
        "unidade_id": porto_alegre['id'],
        "curso_id": prog_web['id'],
        "instrutor_id": gabriel['id'],
        "data_inicio": "2026-02-01",
        "data_fim": "2026-12-31",
        "horario_inicio": "13:30",
        "horario_fim": "17:30",
        "dias_semana": ["segunda", "terca", "quarta", "quinta", "sexta"],
        "vagas_total": 30,
        "ciclo": "01/2026",
        "tipo_turma": "regular"
    },
    {
        "nome": "Programação Web Extensão - Porto Alegre Manhã",
        "unidade_id": porto_alegre['id'],
        "curso_id": prog_web['id'],
        "instrutor_id": ermerson['id'],
        "data_inicio": "2026-02-01",
        "data_fim": "2026-06-30",
        "horario_inicio": "08:00",
        "horario_fim": "12:00",
        "dias_semana": ["segunda", "terca", "quarta", "quinta", "sexta"],
        "vagas_total": 30,
        "ciclo": "01/2026",
        "tipo_turma": "extensao"
    },
    {
        "nome": "Programação Web Extensão - Porto Alegre Tarde",
        "unidade_id": porto_alegre['id'],
        "curso_id": prog_web['id'],
        "instrutor_id": gabriel['id'],
        "data_inicio": "2026-02-01",
        "data_fim": "2026-06-30",
        "horario_inicio": "13:30",
        "horario_fim": "17:30",
        "dias_semana": ["segunda", "terca", "quarta", "quinta", "sexta"],
        "vagas_total": 30,
        "ciclo": "01/2026",
        "tipo_turma": "extensao"
    }
])

# CRIAR AS TURMAS
print(f"\n🎓 Criando {len(turmas_criar)} turmas via API do Render...\n")
criadas = 0
erros = 0

for turma in turmas_criar:
    try:
        response = requests.post(f"{API_URL}/classes", json=turma, headers=headers, timeout=30)
        if response.status_code in [200, 201]:
            print(f"✅ {turma['nome']}")
            criadas += 1
        else:
            print(f"❌ {turma['nome']}: {response.status_code} - {response.text[:100]}")
            erros += 1
    except Exception as e:
        print(f"❌ {turma['nome']}: {e}")
        erros += 1

print(f"\n{'='*60}")
print(f"✅ Criadas: {criadas}")
print(f"❌ Erros: {erros}")
print(f"📊 Total: {len(turmas_criar)}")
