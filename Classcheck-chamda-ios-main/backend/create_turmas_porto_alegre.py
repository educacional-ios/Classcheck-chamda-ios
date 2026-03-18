import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
from datetime import datetime, timezone
import uuid

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME")

async def create_turmas_porto_alegre():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print(f"\n🔍 Conectando em: {DB_NAME}")
    
    # Buscar dados necessários
    unidades = await db.unidades.find().to_list(1000)
    cursos = await db.cursos.find().to_list(1000)
    instrutores = await db.usuarios.find({"tipo": "instrutor"}).to_list(1000)
    
    porto_alegre = next((u for u in unidades if "Porto Alegre" in u.get('nome', '')), None)
    prog_web = next((c for c in cursos if "Programação Web" in c.get('nome', '') and "Noite" not in c.get('nome', '')), None)
    ermerson = next((i for i in instrutores if "ermerson.barros@ios.org.br" in i.get('email', '')), None)
    gabriel = next((i for i in instrutores if "gabriel.bezerra@ios.org.br" in i.get('email', '')), None)
    
    print("\n📍 Dados encontrados:")
    print(f"   Porto Alegre: {porto_alegre.get('nome') if porto_alegre else 'NÃO ENCONTRADA'}")
    print(f"   Programação Web: {prog_web.get('nome') if prog_web else 'NÃO ENCONTRADO'}")
    print(f"   Ermerson: {ermerson.get('nome') if ermerson else 'NÃO ENCONTRADO'}")
    print(f"   Gabriel: {gabriel.get('nome') if gabriel else 'NÃO ENCONTRADO'}")
    
    if not all([porto_alegre, prog_web, ermerson, gabriel]):
        print("\n❌ ERRO: Dados faltando!")
        client.close()
        return
    
    print("\n" + "="*60)
    print("🎓 CRIANDO 4 TURMAS DE PORTO ALEGRE - PROGRAMAÇÃO WEB")
    turmas = []
    
    # 1. Curso Técnico - Manhã (Ermerson)
    turma_tec_manha = {
        "id": str(uuid.uuid4()),
        "nome": "Programação Web Técnico - Porto Alegre Manhã",
        "unidade_id": porto_alegre['id'],
        "curso_id": prog_web['id'],
        "instrutor_id": ermerson['id'],
        "pedagogo_id": None,
        "monitor_id": None,
        "alunos_ids": [],
        "data_inicio": datetime(2026, 2, 1),
        "data_fim": datetime(2026, 12, 31),
        "horario_inicio": "08:00",
        "horario_fim": "12:00",
        "dias_semana": ["segunda", "terca", "quarta", "quinta", "sexta"],
        "vagas_total": 30,
        "vagas_ocupadas": 0,
        "ciclo": "01/2026",
        "tipo_turma": "regular",
        "ativo": True,
        "created_at": datetime.now(timezone.utc)
    }
    turmas.append(turma_tec_manha)
    
    # 2. Curso Técnico - Tarde (Gabriel)
    turma_tec_tarde = {
        "id": str(uuid.uuid4()),
        "nome": "Programação Web Técnico - Porto Alegre Tarde",
        "unidade_id": porto_alegre['id'],
        "curso_id": prog_web['id'],
        "instrutor_id": gabriel['id'],
        "pedagogo_id": None,
        "monitor_id": None,
        "alunos_ids": [],
        "data_inicio": datetime(2026, 2, 1),
        "data_fim": datetime(2026, 12, 31),
        "horario_inicio": "13:30",
        "horario_fim": "17:30",
        "dias_semana": ["segunda", "terca", "quarta", "quinta", "sexta"],
        "vagas_total": 30,
        "vagas_ocupadas": 0,
        "ciclo": "01/2026",
        "tipo_turma": "regular",
        "ativo": True,
        "created_at": datetime.now(timezone.utc)
    }
    turmas.append(turma_tec_tarde)
    
    # 3. Curso Extensão - Manhã (Ermerson)
    turma_ext_manha = {
        "id": str(uuid.uuid4()),
        "nome": "Programação Web Extensão - Porto Alegre Manhã",
        "unidade_id": porto_alegre['id'],
        "curso_id": prog_web['id'],
        "instrutor_id": ermerson['id'],
        "pedagogo_id": None,
        "monitor_id": None,
        "alunos_ids": [],
        "data_inicio": datetime(2026, 2, 1),
        "data_fim": datetime(2026, 6, 30),
        "horario_inicio": "08:00",
        "horario_fim": "12:00",
        "dias_semana": ["segunda", "terca", "quarta", "quinta", "sexta"],
        "vagas_total": 30,
        "vagas_ocupadas": 0,
        "ciclo": "01/2026",
        "tipo_turma": "extensao",
        "ativo": True,
        "created_at": datetime.now(timezone.utc)
    }
    turmas.append(turma_ext_manha)
    
    # 4. Curso Extensão - Tarde (Gabriel)
    turma_ext_tarde = {
        "id": str(uuid.uuid4()),
        "nome": "Programação Web Extensão - Porto Alegre Tarde",
        "unidade_id": porto_alegre['id'],
        "curso_id": prog_web['id'],
        "instrutor_id": gabriel['id'],
        "pedagogo_id": None,
        "monitor_id": None,
        "alunos_ids": [],
        "data_inicio": datetime(2026, 2, 1),
        "data_fim": datetime(2026, 6, 30),
        "horario_inicio": "13:30",
        "horario_fim": "17:30",
        "dias_semana": ["segunda", "terca", "quarta", "quinta", "sexta"],
        "vagas_total": 30,
        "vagas_ocupadas": 0,
        "ciclo": "01/2026",
        "tipo_turma": "extensao",
        "ativo": True,
        "created_at": datetime.now(timezone.utc)
    }
    turmas.append(turma_ext_tarde)
    
    # Inserir as 4 turmas
    await db.turmas.insert_many(turmas)
    
    print(f"\n✅ {len(turmas)} turmas criadas em Porto Alegre:")
    for t in turmas:
        tipo = "TÉCNICO" if t['tipo_turma'] == 'regular' else "EXTENSÃO"
        periodo = "Manhã" if "Manhã" in t['nome'] else "Tarde"
        instrutor = ermerson['nome'] if t['instrutor_id'] == ermerson['id'] else gabriel['nome']
        print(f"   📚 [{tipo}] {periodo} - {t['nome']}")
        print(f"      👨‍🏫 Instrutor: {instrutor}")
        print(f"      🎯 Vagas: {t['vagas_total']}")
        print(f"      📅 {t['data_inicio'].strftime('%d/%m/%Y')} até {t['data_fim'].strftime('%d/%m/%Y')}")
        print(f"      ⏰ {t['horario_inicio']} - {t['horario_fim']}")
        print()
    
    # Verificar total de turmas
    total_turmas = await db.turmas.count_documents({})
    print("="*60)
    print(f"📊 RESUMO GERAL:")
    print(f"   Total de turmas no banco: {total_turmas}")
    
    # Contar por unidade
    turmas_itaquera = await db.turmas.count_documents({"unidade_id": porto_alegre.get('id')})
    print(f"   Turmas em Porto Alegre: {turmas_itaquera}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(create_turmas_porto_alegre())
