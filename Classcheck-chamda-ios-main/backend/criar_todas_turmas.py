import requests
import json

API_URL = "https://sistema-ios-backend.onrender.com/api"

# Login
login_data = {"email": "jesiel.junior@ios.org.br", "senha": "b99018cd"}
login_response = requests.post(f"{API_URL}/auth/login", json=login_data, timeout=30)
token = login_response.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

print("🔐 Login OK!\n")

# Buscar dados
unidades = requests.get(f"{API_URL}/units", headers=headers, timeout=30).json()
cursos = requests.get(f"{API_URL}/courses", headers=headers, timeout=30).json()
usuarios = requests.get(f"{API_URL}/users", headers=headers, timeout=30).json()

# Mapear unidades e cursos
unidades_map = {u['nome']: u['id'] for u in unidades}
cursos_map = {c['nome']: c['id'] for c in cursos}

# Mapear usuários por email
usuarios_map = {u['email']: u for u in usuarios}

# Mapear instrutores e pedagogos específicos
instrutores = {
    'deyverson': next((u['id'] for u in usuarios if 'deyverson' in u.get('email', '').lower()), None),
    'alan': next((u['id'] for u in usuarios if 'alan.oliveira@ios.org.br' == u.get('email')), None),
    'paula': next((u['id'] for u in usuarios if 'paula.silva@ios.org.br' == u.get('email')), None),
    'kaue': next((u['id'] for u in usuarios if 'kaue.pereira@ios.org.br' == u.get('email')), None),
    'andressa': next((u['id'] for u in usuarios if 'andressa.fernandes@ios.org.br' == u.get('email')), None),
    'jesiel': next((u['id'] for u in usuarios if 'jesiel.junior@ios.org.br' == u.get('email') and u.get('tipo') == 'instrutor'), None),  # Jesiel precisa ser instrutor
    'fabiana': next((u['id'] for u in usuarios if 'fabiana' in u.get('email', '').lower()), None),
}

# Se Jesiel não for instrutor, use o padrão mas mostre aviso
if not instrutores['jesiel']:
    print("⚠️  AVISO: Jesiel não é do tipo 'instrutor' no sistema. Usando instrutor padrão para suas turmas.")
    instrutores['jesiel'] = None  # Vai usar o padrão

pedagogos = {
    'elizabete': next((u['id'] for u in usuarios if 'elizabete.cardozo@ios.org.br' == u.get('email')), None),
    'ione': next((u['id'] for u in usuarios if 'samanta.alves@ios.org.br' == u.get('email')), None),  # Ione = Samanta
}

# Instrutor padrão para turmas sem definição
instrutor_padrao = next((u['id'] for u in usuarios if u.get('tipo') == 'instrutor'), None)

if not instrutor_padrao:
    print("ERRO: Nenhum instrutor encontrado!")
    exit()

print(f"✅ Instrutores mapeados: {len([v for v in instrutores.values() if v])}")
print(f"✅ Pedagogos mapeados: {len([v for v in pedagogos.values() if v])}\n")

print("📋 Criando turmas conforme planejamento...\n")

turmas_plano = [
    # BARREIRO BH - Gestão Empresarial com ERP (100 vagas)
    {"unidade": "Barreiro - BH", "curso": "Gestão Empresarial com ERP", "nome": "Gestão Empresarial ERP - Barreiro BH Manhã T1", "periodo": "manhã", "tipo": "regular", "vagas": 25, "inicio": "08:00", "fim": "12:00"},
    {"unidade": "Barreiro - BH", "curso": "Gestão Empresarial com ERP", "nome": "Gestão Empresarial ERP - Barreiro BH Manhã T2", "periodo": "manhã", "tipo": "extensao", "vagas": 25, "inicio": "08:00", "fim": "12:00"},
    {"unidade": "Barreiro - BH", "curso": "Gestão Empresarial com ERP", "nome": "Gestão Empresarial ERP - Barreiro BH Tarde T3", "periodo": "tarde", "tipo": "regular", "vagas": 25, "inicio": "13:00", "fim": "17:00"},
    {"unidade": "Barreiro - BH", "curso": "Gestão Empresarial com ERP", "nome": "Gestão Empresarial ERP - Barreiro BH Tarde T4", "periodo": "tarde", "tipo": "extensao", "vagas": 25, "inicio": "13:00", "fim": "17:00"},
    
    # HORTOLÂNDIA - Suporte TI (40 vagas) - Deyverson instrutor, Elizabete pedagoga
    {"unidade": "Hortolândia", "curso": "Suporte TI", "nome": "Suporte TI - Hortolândia Manhã T1", "periodo": "manhã", "tipo": "regular", "vagas": 20, "inicio": "08:00", "fim": "12:00", "instrutor": "deyverson", "pedagogo": "elizabete"},
    {"unidade": "Hortolândia", "curso": "Suporte TI", "nome": "Suporte TI - Hortolândia Tarde T2", "periodo": "tarde", "tipo": "extensao", "vagas": 20, "inicio": "13:00", "fim": "17:00", "instrutor": "deyverson", "pedagogo": "elizabete"},
    
    # ITAQUERA - Gestão Empresarial com ERP (80 vagas)
    {"unidade": "Itaquera", "curso": "Gestão Empresarial com ERP", "nome": "Gestão Empresarial ERP - Itaquera Manhã T1", "periodo": "manhã", "tipo": "regular", "vagas": 20, "inicio": "08:30", "fim": "11:30"},
    {"unidade": "Itaquera", "curso": "Gestão Empresarial com ERP", "nome": "Gestão Empresarial ERP - Itaquera Manhã T2", "periodo": "manhã", "tipo": "extensao", "vagas": 20, "inicio": "08:30", "fim": "11:30"},
    {"unidade": "Itaquera", "curso": "Gestão Empresarial com ERP", "nome": "Gestão Empresarial ERP - Itaquera Tarde T3", "periodo": "tarde", "tipo": "regular", "vagas": 20, "inicio": "14:00", "fim": "17:00"},
    {"unidade": "Itaquera", "curso": "Gestão Empresarial com ERP", "nome": "Gestão Empresarial ERP - Itaquera Tarde T4", "periodo": "tarde", "tipo": "extensao", "vagas": 20, "inicio": "14:00", "fim": "17:00"},
    
    # JARDIM ÂNGELA - Gestão Empresarial com ERP (80 vagas)
    {"unidade": "Jardim Angela", "curso": "Gestão Empresarial com ERP", "nome": "Gestão Empresarial ERP - Jardim Angela Manhã T1", "periodo": "manhã", "tipo": "regular", "vagas": 20, "inicio": "08:00", "fim": "12:00"},
    {"unidade": "Jardim Angela", "curso": "Gestão Empresarial com ERP", "nome": "Gestão Empresarial ERP - Jardim Angela Manhã T2", "periodo": "manhã", "tipo": "extensao", "vagas": 20, "inicio": "08:00", "fim": "12:00"},
    {"unidade": "Jardim Angela", "curso": "Gestão Empresarial com ERP", "nome": "Gestão Empresarial ERP - Jardim Angela Tarde T3", "periodo": "tarde", "tipo": "regular", "vagas": 20, "inicio": "13:00", "fim": "17:00"},
    {"unidade": "Jardim Angela", "curso": "Gestão Empresarial com ERP", "nome": "Gestão Empresarial ERP - Jardim Angela Tarde T4", "periodo": "tarde", "tipo": "extensao", "vagas": 20, "inicio": "13:00", "fim": "17:00"},
    
    # SANTO AMARO - Programação Web (50 vagas)
    {"unidade": "Santo Amaro", "curso": "Programação Web", "nome": "Programação Web - Santo Amaro Manhã T1", "periodo": "manhã", "tipo": "regular", "vagas": 25, "inicio": "08:00", "fim": "12:00"},
    {"unidade": "Santo Amaro", "curso": "Programação Web", "nome": "Programação Web - Santo Amaro Tarde T2", "periodo": "tarde", "tipo": "regular", "vagas": 25, "inicio": "13:30", "fim": "17:30"},
    
    # PORTO ALEGRE - Programação Web (60 vagas)
    {"unidade": "Porto Alegre", "curso": "Programação Web", "nome": "Programação Web - Porto Alegre Manhã T1", "periodo": "manhã", "tipo": "regular", "vagas": 20, "inicio": "08:00", "fim": "12:00"},
    {"unidade": "Porto Alegre", "curso": "Programação Web", "nome": "Programação Web - Porto Alegre Tarde T2", "periodo": "tarde", "tipo": "regular", "vagas": 20, "inicio": "13:30", "fim": "17:30"},
    {"unidade": "Porto Alegre", "curso": "Programação Web", "nome": "Programação Web - Porto Alegre Tarde T3", "periodo": "tarde", "tipo": "regular", "vagas": 20, "inicio": "18:00", "fim": "22:00"},
    
    # RECIFE - Gestão Empresarial com ERP (80 vagas)
    {"unidade": "Recife", "curso": "Gestão Empresarial com ERP", "nome": "Gestão Empresarial ERP - Recife Manhã T1", "periodo": "manhã", "tipo": "regular", "vagas": 20, "inicio": "08:00", "fim": "12:00"},
    {"unidade": "Recife", "curso": "Gestão Empresarial com ERP", "nome": "Gestão Empresarial ERP - Recife Manhã T2", "periodo": "manhã", "tipo": "extensao", "vagas": 20, "inicio": "08:00", "fim": "12:00"},
    {"unidade": "Recife", "curso": "Gestão Empresarial com ERP", "nome": "Gestão Empresarial ERP - Recife Tarde T3", "periodo": "tarde", "tipo": "regular", "vagas": 20, "inicio": "13:00", "fim": "17:00"},
    {"unidade": "Recife", "curso": "Gestão Empresarial com ERP", "nome": "Gestão Empresarial ERP - Recife Tarde T4", "periodo": "tarde", "tipo": "extensao", "vagas": 20, "inicio": "13:00", "fim": "17:00"},
    
    # SÃO GABRIEL BH - Gestão Empresarial com ERP (100 vagas)
    {"unidade": "São Gabriel - BH", "curso": "Gestão Empresarial com ERP", "nome": "Gestão Empresarial ERP - São Gabriel BH Manhã T1", "periodo": "manhã", "tipo": "regular", "vagas": 25, "inicio": "08:00", "fim": "12:00"},
    {"unidade": "São Gabriel - BH", "curso": "Gestão Empresarial com ERP", "nome": "Gestão Empresarial ERP - São Gabriel BH Manhã T2", "periodo": "manhã", "tipo": "extensao", "vagas": 25, "inicio": "08:00", "fim": "12:00"},
    {"unidade": "São Gabriel - BH", "curso": "Gestão Empresarial com ERP", "nome": "Gestão Empresarial ERP - São Gabriel BH Tarde T3", "periodo": "tarde", "tipo": "regular", "vagas": 25, "inicio": "13:00", "fim": "17:00"},
    {"unidade": "São Gabriel - BH", "curso": "Gestão Empresarial com ERP", "nome": "Gestão Empresarial ERP - São Gabriel BH Tarde T4", "periodo": "tarde", "tipo": "extensao", "vagas": 25, "inicio": "13:00", "fim": "17:00"},
    
    # SEDE SANTANA - Programação Web (50 vagas)
    {"unidade": "Sede Santana", "curso": "Programação Web", "nome": "Programação Web - Sede Santana Manhã T1", "periodo": "manhã", "tipo": "regular", "vagas": 25, "inicio": "08:00", "fim": "12:00"},
    {"unidade": "Sede Santana", "curso": "Programação Web", "nome": "Programação Web - Sede Santana Tarde T2", "periodo": "tarde", "tipo": "regular", "vagas": 25, "inicio": "13:00", "fim": "17:00"},
    
    # SEDE SANTANA - Suporte TI (80 vagas - 4 turmas com 20 alunos cada)
    # Equipes: Alan+Paula e Kauê+Andressa
    {"unidade": "Sede Santana", "curso": "Suporte TI", "nome": "Suporte TI - Sede Santana Manhã T1", "periodo": "manhã", "tipo": "regular", "vagas": 20, "inicio": "08:00", "fim": "12:00", "instrutor": "alan"},
    {"unidade": "Sede Santana", "curso": "Suporte TI", "nome": "Suporte TI - Sede Santana Manhã T2", "periodo": "manhã", "tipo": "extensao", "vagas": 20, "inicio": "08:00", "fim": "12:00", "instrutor": "paula"},
    {"unidade": "Sede Santana", "curso": "Suporte TI", "nome": "Suporte TI - Sede Santana Tarde T3", "periodo": "tarde", "tipo": "regular", "vagas": 20, "inicio": "13:00", "fim": "17:00", "instrutor": "kaue"},
    {"unidade": "Sede Santana", "curso": "Suporte TI", "nome": "Suporte TI - Sede Santana Tarde T4", "periodo": "tarde", "tipo": "extensao", "vagas": 20, "inicio": "13:00", "fim": "17:00", "instrutor": "andressa"},
    
    # SEDE SANTANA - Programação Web Noite (100 vagas - apenas T1 com Jesiel, demais não definidas)
    {"unidade": "Sede Santana", "curso": "Programação Web Noite", "nome": "Programação Web Noite - Sede Santana T1", "periodo": "noite", "tipo": "regular", "vagas": 25, "inicio": "19:00", "fim": "22:00", "instrutor": "jesiel"},
    {"unidade": "Sede Santana", "curso": "Programação Web Noite", "nome": "Programação Web Noite - Sede Santana T2", "periodo": "noite", "tipo": "regular", "vagas": 25, "inicio": "19:00", "fim": "22:00"},
    {"unidade": "Sede Santana", "curso": "Programação Web Noite", "nome": "Programação Web Noite - Sede Santana T3", "periodo": "noite", "tipo": "regular", "vagas": 25, "inicio": "19:00", "fim": "22:00"},
    {"unidade": "Sede Santana", "curso": "Programação Web Noite", "nome": "Programação Web Noite - Sede Santana T4", "periodo": "noite", "tipo": "regular", "vagas": 25, "inicio": "19:00", "fim": "22:00"},
    
    # SEDE SANTANA - Office com Suporte Zendesk (apenas TARDE - 25 vagas)
    # Fabiana instrutora, Ione também é pedagoga
    {"unidade": "Sede Santana", "curso": "Office com Suporte Zendesk", "nome": "Office Zendesk - Sede Santana Tarde T1", "periodo": "tarde", "tipo": "extensao", "vagas": 25, "inicio": "13:00", "fim": "17:00", "instrutor": "fabiana", "pedagogo": "ione"},
    
    # SEDE SANTANA - Análise de Dados e IA (56 vagas)
    {"unidade": "Sede Santana", "curso": "Análise de Dados e Inteligência Artificial aplicada à Sustentabilidade", "nome": "Análise Dados IA - Sede Santana Manhã T1", "periodo": "manhã", "tipo": "regular", "vagas": 28, "inicio": "08:00", "fim": "12:00"},
    {"unidade": "Sede Santana", "curso": "Análise de Dados e Inteligência Artificial aplicada à Sustentabilidade", "nome": "Análise Dados IA - Sede Santana Tarde T2", "periodo": "tarde", "tipo": "extensao", "vagas": 28, "inicio": "13:00", "fim": "17:00"},
    
    # SEDE SANTANA - Power BI (sábado)
    {"unidade": "Sede Santana", "curso": "Power BI", "nome": "Power BI - Sede Santana Sábado T1", "periodo": "sabado", "tipo": "regular", "vagas": 25, "inicio": "08:00", "fim": "12:00"},
    {"unidade": "Sede Santana", "curso": "Power BI", "nome": "Power BI - Sede Santana Sábado T2", "periodo": "sabado", "tipo": "regular", "vagas": 25, "inicio": "13:00", "fim": "17:00"},
    
    # SEDE SANTANA - IA (sábado)
    {"unidade": "Sede Santana", "curso": "IA", "nome": "IA - Sede Santana Sábado T3", "periodo": "sabado", "tipo": "regular", "vagas": 25, "inicio": "08:00", "fim": "12:00"},
    {"unidade": "Sede Santana", "curso": "IA", "nome": "IA - Sede Santana Sábado T4", "periodo": "sabado", "tipo": "regular", "vagas": 25, "inicio": "13:00", "fim": "17:00"},
    
    # SEDE SANTANA - Cyber (sábado)
    {"unidade": "Sede Santana", "curso": "Cyber", "nome": "Cyber - Sede Santana Sábado T5", "periodo": "sabado", "tipo": "regular", "vagas": 25, "inicio": "08:00", "fim": "12:00"},
    {"unidade": "Sede Santana", "curso": "Cyber", "nome": "Cyber - Sede Santana Sábado T6", "periodo": "sabado", "tipo": "regular", "vagas": 25, "inicio": "13:00", "fim": "17:00"},
    
    # SEDE SANTANA - Empreendedorismo (sábado)
    {"unidade": "Sede Santana", "curso": "Empreendedorismo", "nome": "Empreendedorismo - Sede Santana Sábado T7", "periodo": "sabado", "tipo": "regular", "vagas": 25, "inicio": "08:00", "fim": "12:00"},
    {"unidade": "Sede Santana", "curso": "Empreendedorismo", "nome": "Empreendedorismo - Sede Santana Sábado T8", "periodo": "sabado", "tipo": "regular", "vagas": 25, "inicio": "13:00", "fim": "17:00"},
    
    # SEDE SANTANA - Suporte TI verificar (80 vagas)
    {"unidade": "Sede Santana", "curso": "Suporte TI (Verificar curso) e formato", "nome": "Suporte TI Verificar - Sede Santana Manhã T1", "periodo": "manhã", "tipo": "regular", "vagas": 20, "inicio": "08:00", "fim": "12:00"},
    {"unidade": "Sede Santana", "curso": "Suporte TI (Verificar curso) e formato", "nome": "Suporte TI Verificar - Sede Santana Manhã T2", "periodo": "manhã", "tipo": "extensao", "vagas": 20, "inicio": "08:00", "fim": "12:00"},
    {"unidade": "Sede Santana", "curso": "Suporte TI (Verificar curso) e formato", "nome": "Suporte TI Verificar - Sede Santana Tarde T3", "periodo": "tarde", "tipo": "regular", "vagas": 20, "inicio": "13:00", "fim": "17:00"},
    {"unidade": "Sede Santana", "curso": "Suporte TI (Verificar curso) e formato", "nome": "Suporte TI Verificar - Sede Santana Tarde T4", "periodo": "tarde", "tipo": "extensao", "vagas": 20, "inicio": "13:00", "fim": "17:00"},
    
    # SEDE SANTANA - Protheus (50 vagas)
    {"unidade": "Sede Santana", "curso": "Protheus Instalação e Configuração", "nome": "Protheus - Sede Santana Noite T1", "periodo": "noite", "tipo": "regular", "vagas": 25, "inicio": "19:00", "fim": "22:00"},
    {"unidade": "Sede Santana", "curso": "Protheus Instalação e Configuração", "nome": "Protheus - Sede Santana Noite T2", "periodo": "noite", "tipo": "extensao", "vagas": 25, "inicio": "19:00", "fim": "22:00"},
    
    # RIO DE JANEIRO - Gestão Empresarial com ERP (50 vagas)
    {"unidade": "Rio de Janeiro", "curso": "Gestão Empresarial com ERP", "nome": "Gestão Empresarial ERP - Rio de Janeiro Tarde T1", "periodo": "tarde", "tipo": "regular", "vagas": 25, "inicio": "13:00", "fim": "17:00"},
    {"unidade": "Rio de Janeiro", "curso": "Gestão Empresarial com ERP", "nome": "Gestão Empresarial ERP - Rio de Janeiro Tarde T2", "periodo": "tarde", "tipo": "extensao", "vagas": 25, "inicio": "13:00", "fim": "17:00"},
]

print(f"📊 Total de turmas a criar: {len(turmas_plano)}\n")

# Primeiro, deletar todas as turmas existentes
print("🗑️ Limpando turmas existentes...")
turmas_antigas = requests.get(f"{API_URL}/classes", headers=headers, timeout=30).json()
for turma in turmas_antigas:
    try:
        requests.delete(f"{API_URL}/classes/{turma['id']}", headers=headers, timeout=30)
        print(f"   ❌ Deletada: {turma['nome']}")
    except:
        pass

print(f"\n✅ Limpeza concluída! Criando {len(turmas_plano)} novas turmas...\n")

# Criar todas as turmas
criadas = 0
erros = 0

for turma_plan in turmas_plano:
    unidade_id = unidades_map.get(turma_plan['unidade'])
    curso_id = cursos_map.get(turma_plan['curso'])
    
    if not unidade_id or not curso_id:
        print(f"❌ {turma_plan['nome']}: Unidade ou curso não encontrado")
        erros += 1
        continue
    
    # Determinar instrutor e pedagogo
    instrutor_id = instrutor_padrao
    if 'instrutor' in turma_plan and turma_plan['instrutor'] in instrutores:
        instrutor_id = instrutores[turma_plan['instrutor']] or instrutor_padrao
    
    pedagogo_id = None
    if 'pedagogo' in turma_plan and turma_plan['pedagogo'] in pedagogos:
        pedagogo_id = pedagogos[turma_plan['pedagogo']]
    
    turma_data = {
        "nome": turma_plan['nome'],
        "unidade_id": unidade_id,
        "curso_id": curso_id,
        "instrutor_id": instrutor_id,
        "data_inicio": "2026-02-01",
        "data_fim": "2026-12-31" if turma_plan['tipo'] == 'regular' else "2026-06-30",
        "horario_inicio": turma_plan['inicio'],
        "horario_fim": turma_plan['fim'],
        "dias_semana": ["sabado"] if turma_plan['periodo'] == 'sabado' else ["segunda", "terca", "quarta", "quinta", "sexta"],
        "vagas_total": turma_plan['vagas'],
        "ciclo": "01/2026",
        "tipo_turma": turma_plan['tipo']
    }
    
    # Adicionar pedagogo se definido
    if pedagogo_id:
        turma_data["pedagogo_id"] = pedagogo_id
    
    try:
        response = requests.post(f"{API_URL}/classes", json=turma_data, headers=headers, timeout=30)
        if response.status_code in [200, 201]:
            instrutor_nome = turma_plan.get('instrutor', 'padrão')
            pedagogo_nome = turma_plan.get('pedagogo', '')
            info = f" (Inst: {instrutor_nome}" + (f", Ped: {pedagogo_nome}" if pedagogo_nome else "") + ")"
            print(f"✅ {turma_plan['nome']}{info}")
            criadas += 1
        else:
            print(f"❌ {turma_plan['nome']}: {response.status_code} - {response.text[:200]}")
            erros += 1
    except Exception as e:
        print(f"❌ {turma_plan['nome']}: {e}")
        erros += 1

print(f"\n{'='*60}")
print(f"✅ Criadas: {criadas}")
print(f"❌ Erros: {erros}")
print(f"📊 Total planejado: {len(turmas_plano)}")
print(f"\n🎯 VAGAS TOTAIS CRIADAS: {sum(t['vagas'] for t in turmas_plano)}")
