import asyncio
import uuid
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

# Lista de turmas a criar
TURMAS_PARA_CRIAR = [
    {"nome": "Gestão Empresarial ERP - Barreiro BH Manhã T1", "tipo": "Regular", "ciclo": "01/2026", "periodo": "31/01/2026 - 30/12/2026", "horario": "08:00 - 12:00", "vagas": 25},
    {"nome": "Gestão Empresarial ERP - Barreiro BH Manhã T2", "tipo": "Extensão", "ciclo": "01/2026", "periodo": "31/01/2026 - 29/06/2026", "horario": "08:00 - 12:00", "vagas": 25},
    {"nome": "Gestão Empresarial ERP - Barreiro BH Tarde T3", "tipo": "Regular", "ciclo": "01/2026", "periodo": "31/01/2026 - 30/12/2026", "horario": "13:00 - 17:00", "vagas": 25},
    {"nome": "Gestão Empresarial ERP - Barreiro BH Tarde T4", "tipo": "Extensão", "ciclo": "01/2026", "periodo": "31/01/2026 - 29/06/2026", "horario": "13:00 - 17:00", "vagas": 25},
    {"nome": "Suporte TI - Hortolândia Manhã T1", "tipo": "Regular", "ciclo": "01/2026", "periodo": "31/01/2026 - 30/12/2026", "horario": "08:00 - 12:00", "vagas": 20},
    {"nome": "Suporte TI - Hortolândia Tarde T2", "tipo": "Regular", "ciclo": "01/2026", "periodo": "31/01/2026 - 29/06/2026", "horario": "13:00 - 17:00", "vagas": 20},
    {"nome": "Gestão Empresarial ERP - Jardim Angela Manhã T1", "tipo": "Regular", "ciclo": "01/2026", "periodo": "31/01/2026 - 30/12/2026", "horario": "08:00 - 12:00", "vagas": 20},
    {"nome": "Gestão Empresarial ERP - Jardim Angela Manhã T2", "tipo": "Extensão", "ciclo": "01/2026", "periodo": "31/01/2026 - 29/06/2026", "horario": "08:00 - 12:00", "vagas": 20},
    {"nome": "Gestão Empresarial ERP - Jardim Angela Tarde T3", "tipo": "Regular", "ciclo": "01/2026", "periodo": "31/01/2026 - 30/12/2026", "horario": "13:00 - 17:00", "vagas": 20},
    {"nome": "Gestão Empresarial ERP - Jardim Angela Tarde T4", "tipo": "Extensão", "ciclo": "01/2026", "periodo": "31/01/2026 - 29/06/2026", "horario": "13:00 - 17:00", "vagas": 20},
    {"nome": "Programação Web - Santo Amaro Manhã T1", "tipo": "Regular", "ciclo": "01/2026", "periodo": "31/01/2026 - 30/12/2026", "horario": "08:00 - 12:00", "vagas": 25},
    {"nome": "Programação Web - Santo Amaro Tarde T2", "tipo": "Regular", "ciclo": "01/2026", "periodo": "31/01/2026 - 30/12/2026", "horario": "13:30 - 17:30", "vagas": 25},
    {"nome": "Programação Web - Porto Alegre Manhã T1", "tipo": "Regular", "ciclo": "01/2026", "periodo": "31/01/2026 - 30/12/2026", "horario": "08:00 - 12:00", "vagas": 20},
    {"nome": "Programação Web - Porto Alegre Tarde T2", "tipo": "Extensão", "ciclo": "01/2026", "periodo": "31/01/2026 - 30/12/2026", "horario": "08:00 - 12:00", "vagas": 20},
    {"nome": "Programação Web - Porto Alegre Tarde T3", "tipo": "Regular", "ciclo": "01/2026", "periodo": "31/01/2026 - 30/12/2026", "horario": "13:00 - 17:00", "vagas": 20},
    {"nome": "Gestão Empresarial ERP - Recife Manhã T1", "tipo": "Regular", "ciclo": "01/2026", "periodo": "31/01/2026 - 30/12/2026", "horario": "08:00 - 12:00", "vagas": 20},
    {"nome": "Gestão Empresarial ERP - Recife Manhã T2", "tipo": "Regular", "ciclo": "01/2026", "periodo": "31/01/2026 - 29/06/2026", "horario": "08:00 - 12:00", "vagas": 20},
    {"nome": "Gestão Empresarial ERP - Recife Tarde T3", "tipo": "Regular", "ciclo": "01/2026", "periodo": "31/01/2026 - 30/12/2026", "horario": "13:00 - 17:00", "vagas": 20},
    {"nome": "Gestão Empresarial ERP - Recife Tarde T4", "tipo": "Regular", "ciclo": "01/2026", "periodo": "31/01/2026 - 29/06/2026", "horario": "13:00 - 17:00", "vagas": 20},
    {"nome": "Gestão Empresarial ERP - São Gabriel BH Manhã T1", "tipo": "Regular", "ciclo": "01/2026", "periodo": "31/01/2026 - 30/12/2026", "horario": "08:00 - 12:00", "vagas": 25},
    {"nome": "Gestão Empresarial ERP - São Gabriel BH Manhã T2", "tipo": "Extensão", "ciclo": "01/2026", "periodo": "31/01/2026 - 29/06/2026", "horario": "08:00 - 12:00", "vagas": 25},
    {"nome": "Gestão Empresarial ERP - São Gabriel BH Tarde T3", "tipo": "Regular", "ciclo": "01/2026", "periodo": "31/01/2026 - 30/12/2026", "horario": "13:00 - 17:00", "vagas": 25},
    {"nome": "Gestão Empresarial ERP - São Gabriel BH Tarde T4", "tipo": "Extensão", "ciclo": "01/2026", "periodo": "31/01/2026 - 29/06/2026", "horario": "13:00 - 17:00", "vagas": 25},
    {"nome": "Programação Web - Sede Santana Manhã T1", "tipo": "Regular", "ciclo": "01/2026", "periodo": "31/01/2026 - 30/12/2026", "horario": "08:00 - 12:00", "vagas": 25},
    {"nome": "Programação Web - Sede Santana Tarde T2", "tipo": "Regular", "ciclo": "01/2026", "periodo": "31/01/2026 - 30/12/2026", "horario": "13:00 - 17:00", "vagas": 25},
    {"nome": "Suporte TI - Sede Santana Manhã T1", "tipo": "Regular", "ciclo": "01/2026", "periodo": "08/03/2026 - 30/12/2026", "horario": "08:00 - 12:00", "vagas": 20},
    {"nome": "Suporte TI - Sede Santana Manhã T2", "tipo": "Extensão", "ciclo": "01/2026", "periodo": "31/01/2026 - 29/06/2026", "horario": "08:00 - 12:00", "vagas": 20},
    {"nome": "Suporte TI - Sede Santana Tarde T3", "tipo": "Regular", "ciclo": "01/2026", "periodo": "08/03/2026 - 30/12/2026", "horario": "13:00 - 17:00", "vagas": 20},
    {"nome": "Suporte TI - Sede Santana Tarde T4", "tipo": "Extensão", "ciclo": "01/2026", "periodo": "31/01/2026 - 29/06/2026", "horario": "13:00 - 17:00", "vagas": 20},
    {"nome": "Programação Web Noite - Sede Santana T1", "tipo": "Regular", "ciclo": "01/2026", "periodo": "31/01/2026 - 30/12/2026", "horario": "19:00 - 22:00", "vagas": 25},
    {"nome": "Programação Web Noite - Sede Santana T2", "tipo": "Regular", "ciclo": "01/2026", "periodo": "31/01/2026 - 30/12/2026", "horario": "19:00 - 22:00", "vagas": 25},
    {"nome": "Programação Web Noite - Sede Santana T3", "tipo": "Regular", "ciclo": "01/2026", "periodo": "31/01/2026 - 30/12/2026", "horario": "19:00 - 22:00", "vagas": 25},
    {"nome": "Programação Web Noite - Sede Santana T4", "tipo": "Regular", "ciclo": "01/2026", "periodo": "31/01/2026 - 30/12/2026", "horario": "19:00 - 22:00", "vagas": 25},
    {"nome": "Office Zendesk - Sede Santana Tarde T1", "tipo": "Regular", "ciclo": "01/2026", "periodo": "31/01/2026 - 29/06/2026", "horario": "13:00 - 17:00", "vagas": 25},
    {"nome": "Análise Dados IA - Sede Santana Manhã T1", "tipo": "Regular", "ciclo": "01/2026", "periodo": "31/01/2026 - 30/12/2026", "horario": "08:00 - 12:00", "vagas": 28},
    {"nome": "Análise Dados IA - Sede Santana Tarde T2", "tipo": "Regular", "ciclo": "01/2026", "periodo": "31/01/2026 - 29/06/2026", "horario": "13:00 - 17:00", "vagas": 28},
    {"nome": "Power BI - Sede Santana Sábado T1", "tipo": "Regular", "ciclo": "01/2026", "periodo": "31/01/2026 - 30/12/2026", "horario": "08:00 - 12:00", "vagas": 25},
    {"nome": "Power BI - Sede Santana Sábado T2", "tipo": "Regular", "ciclo": "01/2026", "periodo": "31/01/2026 - 30/12/2026", "horario": "13:00 - 17:00", "vagas": 25},
    {"nome": "IA - Sede Santana Sábado T3", "tipo": "Regular", "ciclo": "01/2026", "periodo": "31/01/2026 - 30/12/2026", "horario": "08:00 - 12:00", "vagas": 25},
    {"nome": "IA - Sede Santana Sábado T4", "tipo": "Regular", "ciclo": "01/2026", "periodo": "31/01/2026 - 30/12/2026", "horario": "13:00 - 17:00", "vagas": 25},
    {"nome": "Cyber - Sede Santana Sábado T5", "tipo": "Regular", "ciclo": "01/2026", "periodo": "31/01/2026 - 30/12/2026", "horario": "08:00 - 12:00", "vagas": 25},
    {"nome": "Cyber - Sede Santana Sábado T6", "tipo": "Regular", "ciclo": "01/2026", "periodo": "31/01/2026 - 30/12/2026", "horario": "13:00 - 17:00", "vagas": 25},
    {"nome": "Empreendedorismo - Sede Santana Sábado T7", "tipo": "Regular", "ciclo": "01/2026", "periodo": "31/01/2026 - 30/12/2026", "horario": "08:00 - 12:00", "vagas": 25},
    {"nome": "Empreendedorismo - Sede Santana Sábado T8", "tipo": "Regular", "ciclo": "01/2026", "periodo": "31/01/2026 - 30/12/2026", "horario": "13:00 - 17:00", "vagas": 25},
    {"nome": "Suporte TI 2 - Sede Santana Manhã T1", "tipo": "Regular", "ciclo": "01/2026", "periodo": "31/01/2026 - 30/12/2026", "horario": "08:00 - 12:00", "vagas": 20},
    {"nome": "Suporte TI 2 - Sede Santana Manhã T2", "tipo": "Extensão", "ciclo": "01/2026", "periodo": "31/01/2026 - 29/06/2026", "horario": "08:00 - 12:00", "vagas": 20},
    {"nome": "Suporte TI 2 - Sede Santana Tarde T3", "tipo": "Regular", "ciclo": "01/2026", "periodo": "31/01/2026 - 30/12/2026", "horario": "13:00 - 17:00", "vagas": 20},
    {"nome": "Suporte TI 2 - Sede Santana Tarde T4", "tipo": "Extensão", "ciclo": "01/2026", "periodo": "31/01/2026 - 29/06/2026", "horario": "13:00 - 17:00", "vagas": 20},
    {"nome": "Protheus - Sede Santana Noite T1", "tipo": "Regular", "ciclo": "01/2026", "periodo": "31/01/2026 - 30/12/2026", "horario": "19:00 - 22:00", "vagas": 25},
    {"nome": "Protheus - Sede Santana Noite T2", "tipo": "Regular", "ciclo": "01/2026", "periodo": "31/01/2026 - 29/06/2026", "horario": "19:00 - 22:00", "vagas": 25},
    {"nome": "Gestão Empresarial ERP - Rio de Janeiro Tarde T1", "tipo": "Regular", "ciclo": "01/2026", "periodo": "31/01/2026 - 30/12/2026", "horario": "13:00 - 17:00", "vagas": 25},
    {"nome": "Gestão Empresarial ERP - Rio de Janeiro Tarde T2", "tipo": "Regular", "ciclo": "01/2026", "periodo": "31/01/2026 - 29/06/2026", "horario": "13:00 - 17:00", "vagas": 25},
]

async def criar_turmas_faltantes():
    MONGODB_URL = "mongodb+srv://educacional_db_user:qpvR7mlOHSoxwvQ8@chamada-prod.nr10evs.mongodb.net/IOS-SISTEMA-CHAMADA?retryWrites=true&w=majority&appName=chamada-prod"
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client["IOS-SISTEMA-CHAMADA"]
    
    print(f"\n{'='*60}")
    print("🆕 CRIANDO TURMAS FALTANTES")
    print(f"{'='*60}\n")
    
    # Obter unidade e curso padrão (usar primeiro de cada)
    unidades = await db.unidades.find({"ativo": True}).to_list(10)
    cursos = await db.cursos.find({"ativo": True}).to_list(20)
    
    if not unidades or not cursos:
        print("❌ Erro: Nenhuma unidade ou curso encontrado no banco")
        return
    
    unidade_padrao = unidades[0]
    curso_padrao = cursos[0]
    
    print(f"📍 Unidade padrão: {unidade_padrao.get('nome')}")
    print(f"📚 Curso padrão: {curso_padrao.get('nome')}\n")
    
    criadas = 0
    ja_existentes = 0
    
    for info_turma in TURMAS_PARA_CRIAR:
        # Verificar se já existe
        existe = await db.turmas.find_one({"nome": info_turma["nome"]})
        
        if existe:
            print(f"⏭️  Turma já existe: {info_turma['nome']}")
            ja_existentes += 1
            continue
        
        # Parsear período
        periodo_parts = info_turma["periodo"].split(" - ")
        data_inicio = datetime.strptime(periodo_parts[0], "%d/%m/%Y").date().isoformat()
        data_fim = datetime.strptime(periodo_parts[1], "%d/%m/%Y").date().isoformat()
        
        # Parsear horário
        horario_parts = info_turma["horario"].split(" - ")
        hora_inicio = horario_parts[0]
        hora_fim = horario_parts[1]
        
        # Criar turma
        turma = {
            "id": str(uuid.uuid4()),
            "nome": info_turma["nome"],
            "unidade_id": unidade_padrao.get("id"),
            "unidade_nome": unidade_padrao.get("nome"),
            "curso_id": curso_padrao.get("id"),
            "curso_nome": curso_padrao.get("nome"),
            "instrutor_ids": [],  # Array vazio - admin pode atribuir depois
            "alunos_ids": [],
            "tipo": info_turma["tipo"],
            "ciclo": info_turma["ciclo"],
            "data_inicio": data_inicio,
            "data_fim": data_fim,
            "hora_inicio": hora_inicio,
            "hora_fim": hora_fim,
            "vagas": info_turma["vagas"],
            "ativo": True,
            "criado_em": datetime.utcnow().isoformat()
        }
        
        await db.turmas.insert_one(turma)
        print(f"✅ Criada: {info_turma['nome']}")
        criadas += 1
    
    print(f"\n{'='*60}")
    print(f"✅ CONCLUÍDO:")
    print(f"   Turmas criadas: {criadas}")
    print(f"   Já existentes: {ja_existentes}")
    print(f"   Total: {criadas + ja_existentes}")
    print(f"{'='*60}\n")
    
    # Verificar total final
    total_final = await db.turmas.count_documents({})
    print(f"📊 Total de turmas no banco agora: {total_final}\n")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(criar_turmas_faltantes())
