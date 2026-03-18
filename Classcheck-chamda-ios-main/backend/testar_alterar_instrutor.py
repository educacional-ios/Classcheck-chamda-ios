import requests

API_URL = "https://sistema-ios-backend.onrender.com/api"

# Login
print("🔐 Fazendo login...")
login_data = {"email": "jesiel.junior@ios.org.br", "senha": "b99018cd"}
login_response = requests.post(f"{API_URL}/auth/login", json=login_data, timeout=30)
token = login_response.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}
print("✅ Login OK!\n")

# Buscar primeira turma
print("📋 Buscando turmas...")
turmas = requests.get(f"{API_URL}/classes", headers=headers, timeout=30).json()
if not turmas:
    print("❌ Nenhuma turma encontrada!")
    exit()

primeira_turma = turmas[0]
print(f"Turma selecionada: {primeira_turma['nome']}")
print(f"Instrutor atual: {primeira_turma.get('instrutor_id', 'Não definido')}\n")

# Buscar instrutores disponíveis
print("👥 Buscando instrutores...")
usuarios = requests.get(f"{API_URL}/users", headers=headers, timeout=30).json()
instrutores = [u for u in usuarios if u.get('tipo') == 'instrutor']

if len(instrutores) < 2:
    print("❌ Precisa de pelo menos 2 instrutores para testar!")
    exit()

# Pegar um instrutor diferente do atual
novo_instrutor = None
for instrutor in instrutores:
    if instrutor['id'] != primeira_turma.get('instrutor_id'):
        novo_instrutor = instrutor
        break

if not novo_instrutor:
    novo_instrutor = instrutores[1] if len(instrutores) > 1 else instrutores[0]

print(f"Novo instrutor: {novo_instrutor['nome']} ({novo_instrutor['id']})\n")

# Tentar alterar o instrutor
print("🔄 Tentando alterar instrutor da turma...")
dados_atualizacao = {
    "nome": primeira_turma['nome'],
    "unidade_id": primeira_turma['unidade_id'],
    "curso_id": primeira_turma['curso_id'],
    "instrutor_id": novo_instrutor['id'],  # MUDANDO O INSTRUTOR
    "data_inicio": primeira_turma['data_inicio'],
    "data_fim": primeira_turma['data_fim'],
    "horario_inicio": primeira_turma['horario_inicio'],
    "horario_fim": primeira_turma['horario_fim'],
    "dias_semana": primeira_turma['dias_semana'],
    "vagas_total": primeira_turma['vagas_total'],
    "ciclo": primeira_turma['ciclo'],
    "tipo_turma": primeira_turma.get('tipo_turma', 'regular')
}

print(f"Dados enviados: {dados_atualizacao}\n")

try:
    response = requests.put(
        f"{API_URL}/classes/{primeira_turma['id']}", 
        json=dados_atualizacao, 
        headers=headers, 
        timeout=30
    )
    
    if response.status_code in [200, 201]:
        print("✅ SUCESSO! Instrutor alterado com sucesso!")
        print(f"Resposta: {response.json()}")
    else:
        print(f"❌ ERRO! Status: {response.status_code}")
        print(f"Resposta: {response.text}")
except Exception as e:
    print(f"❌ EXCEÇÃO: {e}")
