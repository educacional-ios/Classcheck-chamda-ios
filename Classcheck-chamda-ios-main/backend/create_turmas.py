import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
from datetime import datetime, date, timezone
import uuid

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME")

async def create_turmas():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print(f"\n🔍 Conectando em: {DB_NAME}")
    
    # Verificar unidades existentes
    print("\n📍 Unidades disponíveis:")
    unidades = await db.unidades.find().to_list(1000)
    for unidade in unidades:
        print(f"   - {unidade.get('nome')} (ID: {unidade.get('id')})")
    
    # Verificar cursos existentes
    print("\n📚 Cursos disponíveis:")
    cursos = await db.cursos.find().to_list(1000)
    for curso in cursos:
        print(f"   - {curso.get('nome')} (ID: {curso.get('id')})")
    
    # Verificar instrutores existentes
    print("\n👨‍🏫 Instrutores disponíveis:")
    instrutores = await db.usuarios.find({"tipo": "instrutor"}).to_list(1000)
    for instrutor in instrutores:
        print(f"   - {instrutor.get('nome')} ({instrutor.get('email')}) - ID: {instrutor.get('id')}")
    
    # Verificar pedagogos existentes
    print("\n👩‍🎓 Pedagogos disponíveis:")
    pedagogos = await db.usuarios.find({"tipo": "pedagogo"}).to_list(1000)
    for pedagogo in pedagogos:
        print(f"   - {pedagogo.get('nome')} ({pedagogo.get('email')}) - ID: {pedagogo.get('id')}")
    
    # Buscar IDs específicos
    itaquera = next((u for u in unidades if "Itaquera" in u.get('nome', '')), None)
    santo_amaro = next((u for u in unidades if "Santo Amaro" in u.get('nome', '')), None)
    porto_alegre = next((u for u in unidades if "Porto Alegre" in u.get('nome', '')), None)
    
    erp_curso = next((c for c in cursos if "ERP" in c.get('nome', '') or "Gestão Empresarial" in c.get('nome', '')), None)
    
    jose_marcos = next((i for i in instrutores if "jose.marcos@ios.org.br" in i.get('email', '')), None)
    graziela = next((i for i in instrutores if "graziela.santos@ios.org.br" in i.get('email', '')), None)
    lise = next((i for i in instrutores if "lise.chaves@ios.org.br" in i.get('email', '')), None)
    ermerson = next((i for i in instrutores if "ermerson.barros@ios.org.br" in i.get('email', '')), None)
    gabriel = next((i for i in instrutores if "gabriel" in i.get('email', '').lower()), None)
    
    print("\n" + "="*60)
    print("🔍 Verificando dados encontrados:")
    print(f"   Itaquera: {itaquera.get('nome') if itaquera else 'NÃO ENCONTRADA'}")
    print(f"   Santo Amaro: {santo_amaro.get('nome') if santo_amaro else 'NÃO ENCONTRADA'}")
    print(f"   Porto Alegre: {porto_alegre.get('nome') if porto_alegre else 'NÃO ENCONTRADA'}")
    print(f"   Curso ERP: {erp_curso.get('nome') if erp_curso else 'NÃO ENCONTRADO'}")
    print(f"   José Marcos: {jose_marcos.get('nome') if jose_marcos else 'NÃO ENCONTRADO'}")
    print(f"   Graziela: {graziela.get('nome') if graziela else 'NÃO ENCONTRADA'}")
    print(f"   Lise: {lise.get('nome') if lise else 'NÃO ENCONTRADA'}")
    print(f"   Ermerson: {ermerson.get('nome') if ermerson else 'NÃO ENCONTRADO'}")
    print(f"   Gabriel: {gabriel.get('nome') if gabriel else 'NÃO ENCONTRADO'}")
    
    # Verificar se temos os dados necessários
    missing = []
    if not itaquera: missing.append("Unidade Itaquera")
    if not santo_amaro: missing.append("Unidade Santo Amaro")
    if not porto_alegre: missing.append("Unidade Porto Alegre")
    if not erp_curso: missing.append("Curso de Gestão Empresarial ERP")
    if not jose_marcos: missing.append("Instrutor José Marcos")
    if not graziela: missing.append("Instrutora Graziela")
    if not lise: missing.append("Instrutora Lise")
    if not ermerson: missing.append("Instrutor Ermerson")
    
    if missing:
        print(f"\n❌ DADOS FALTANDO: {', '.join(missing)}")
        print("\n⚠️ PRECISO CRIAR ESSES DADOS PRIMEIRO!")
        resposta = input("\nDeseja que eu crie os dados faltantes? (s/n): ")
        if resposta.lower() == 's':
            await criar_dados_faltantes(db, missing, unidades, cursos, instrutores)
        else:
            client.close()
            return
    
    # Criar turmas de Itaquera
    if itaquera and erp_curso and jose_marcos:
        print("\n" + "="*60)
        print("🎓 CRIANDO TURMAS DE ITAQUERA")
        turmas_itaquera = []
        
        # 2 turmas no período da manhã (8:30-11:30)
        for i in range(1, 3):
            turma = {
                "id": str(uuid.uuid4()),
                "nome": f"Gestão Empresarial ERP - Itaquera Manhã T{i}",
                "unidade_id": itaquera['id'],
                "curso_id": erp_curso['id'],
                "instrutor_id": jose_marcos['id'],
                "pedagogo_id": None,
                "monitor_id": None,
                "alunos_ids": [],
                "data_inicio": datetime(2026, 2, 1),  # Primeiro semestre 2026
                "data_fim": datetime(2026, 6, 30),
                "horario_inicio": "08:30",
                "horario_fim": "11:30",
                "dias_semana": ["segunda", "terca", "quarta", "quinta"],  # Híbrido
                "vagas_total": 20,
                "vagas_ocupadas": 0,
                "ciclo": "01/2026",
                "tipo_turma": "regular",
                "ativo": True,
                "created_at": datetime.now(timezone.utc)
            }
            turmas_itaquera.append(turma)
        
        # 2 turmas no período da tarde (14:00-17:00)
        for i in range(1, 3):
            turma = {
                "id": str(uuid.uuid4()),
                "nome": f"Gestão Empresarial ERP - Itaquera Tarde T{i}",
                "unidade_id": itaquera['id'],
                "curso_id": erp_curso['id'],
                "instrutor_id": jose_marcos['id'],
                "pedagogo_id": None,
                "monitor_id": None,
                "alunos_ids": [],
                "data_inicio": datetime(2026, 2, 1),
                "data_fim": datetime(2026, 6, 30),
                "horario_inicio": "14:00",
                "horario_fim": "17:00",
                "dias_semana": ["segunda", "terca", "quarta", "quinta"],
                "vagas_total": 20,
                "vagas_ocupadas": 0,
                "ciclo": "01/2026",
                "tipo_turma": "regular",
                "ativo": True,
                "created_at": datetime.now(timezone.utc)
            }
            turmas_itaquera.append(turma)
        
        await db.turmas.insert_many(turmas_itaquera)
        print(f"   ✅ {len(turmas_itaquera)} turmas criadas em Itaquera")
        for t in turmas_itaquera:
            print(f"      - {t['nome']}")
    
    # Criar turmas de Santo Amaro
    if santo_amaro and erp_curso and graziela and lise:
        print("\n" + "="*60)
        print("🎓 CRIANDO TURMAS DE SANTO AMARO")
        turmas_santo_amaro = []
        
        # Turma manhã com Graziela
        turma_manha = {
            "id": str(uuid.uuid4()),
            "nome": "Gestão Empresarial ERP - Santo Amaro Manhã",
            "unidade_id": santo_amaro['id'],
            "curso_id": erp_curso['id'],
            "instrutor_id": graziela['id'],
            "pedagogo_id": None,
            "monitor_id": None,
            "alunos_ids": [],
            "data_inicio": datetime(2026, 2, 1),
            "data_fim": datetime(2026, 6, 30),
            "horario_inicio": "08:00",
            "horario_fim": "12:00",
            "dias_semana": ["segunda", "terca", "quarta", "quinta", "sexta"],
            "vagas_total": 25,
            "vagas_ocupadas": 0,
            "ciclo": "01/2026",
            "tipo_turma": "regular",
            "ativo": True,
            "created_at": datetime.now(timezone.utc)
        }
        turmas_santo_amaro.append(turma_manha)
        
        # Turma tarde com Lise
        turma_tarde = {
            "id": str(uuid.uuid4()),
            "nome": "Gestão Empresarial ERP - Santo Amaro Tarde",
            "unidade_id": santo_amaro['id'],
            "curso_id": erp_curso['id'],
            "instrutor_id": lise['id'],
            "pedagogo_id": None,
            "monitor_id": None,
            "alunos_ids": [],
            "data_inicio": datetime(2026, 2, 1),
            "data_fim": datetime(2026, 6, 30),
            "horario_inicio": "13:30",
            "horario_fim": "17:30",
            "dias_semana": ["segunda", "terca", "quarta", "quinta", "sexta"],
            "vagas_total": 25,
            "vagas_ocupadas": 0,
            "ciclo": "01/2026",
            "tipo_turma": "regular",
            "ativo": True,
            "created_at": datetime.now(timezone.utc)
        }
        turmas_santo_amaro.append(turma_tarde)
        
        await db.turmas.insert_many(turmas_santo_amaro)
        print(f"   ✅ {len(turmas_santo_amaro)} turmas criadas em Santo Amaro")
        for t in turmas_santo_amaro:
            print(f"      - {t['nome']}")
    
    # Criar turmas de Porto Alegre
    if porto_alegre and ermerson:
        print("\n" + "="*60)
        print("🎓 CRIANDO TURMAS DE PORTO ALEGRE")
        
        # Primeiro, precisamos verificar se há curso técnico e curso de extensão
        print("\n⚠️ PERGUNTA: Qual o nome do curso técnico e do curso de extensão para Porto Alegre?")
        print("   Cursos disponíveis:")
        for curso in cursos:
            print(f"      - {curso.get('nome')} (ID: {curso.get('id')})")
        
        print("\n❓ Preciso saber qual curso usar para:")
        print("   1. Curso Técnico (2 turmas)")
        print("   2. Curso de Extensão (2 turmas)")
        print("\nPor favor, me informe os nomes dos cursos para continuar.")
    
    print("\n" + "="*60)
    print("✅ PROCESSO CONCLUÍDO!")
    
    # Mostrar resumo
    total_turmas = await db.turmas.count_documents({})
    print(f"\n📊 Total de turmas no banco: {total_turmas}")
    
    client.close()

async def criar_dados_faltantes(db, missing, unidades, cursos, instrutores):
    """Cria unidades, cursos ou instrutores que estão faltando"""
    
    # Criar unidades
    if "Unidade Itaquera" in missing:
        print("\n📍 Criando Unidade Itaquera...")
        itaquera = {
            "id": str(uuid.uuid4()),
            "nome": "Itaquera",
            "endereco": "Itaquera, São Paulo - SP",
            "ativa": True,
            "created_at": datetime.now(timezone.utc)
        }
        await db.unidades.insert_one(itaquera)
        print(f"   ✅ Unidade Itaquera criada (ID: {itaquera['id']})")
    
    if "Unidade Santo Amaro" in missing:
        print("\n📍 Criando Unidade Santo Amaro...")
        santo_amaro = {
            "id": str(uuid.uuid4()),
            "nome": "Santo Amaro",
            "endereco": "Santo Amaro, São Paulo - SP",
            "ativa": True,
            "created_at": datetime.now(timezone.utc)
        }
        await db.unidades.insert_one(santo_amaro)
        print(f"   ✅ Unidade Santo Amaro criada (ID: {santo_amaro['id']})")
    
    if "Unidade Porto Alegre" in missing:
        print("\n📍 Criando Unidade Porto Alegre...")
        porto_alegre = {
            "id": str(uuid.uuid4()),
            "nome": "Porto Alegre",
            "endereco": "Porto Alegre - RS",
            "ativa": True,
            "created_at": datetime.now(timezone.utc)
        }
        await db.unidades.insert_one(porto_alegre)
        print(f"   ✅ Unidade Porto Alegre criada (ID: {porto_alegre['id']})")
    
    # Criar curso de Gestão Empresarial ERP
    if "Curso de Gestão Empresarial ERP" in missing:
        print("\n📚 Criando Curso de Gestão Empresarial ERP...")
        erp_curso = {
            "id": str(uuid.uuid4()),
            "nome": "Gestão Empresarial ERP",
            "descricao": "Curso de Gestão Empresarial com foco em ERP",
            "carga_horaria": 800,
            "ativo": True,
            "created_at": datetime.now(timezone.utc)
        }
        await db.cursos.insert_one(erp_curso)
        print(f"   ✅ Curso criado (ID: {erp_curso['id']})")
    
    # Criar instrutores
    if "Instrutor José Marcos" in missing:
        print("\n👨‍🏫 Criando instrutor José Marcos...")
        jose_marcos = {
            "id": str(uuid.uuid4()),
            "nome": "José Marcos Valério da Silva",
            "email": "jose.marcos@ios.org.br",
            "senha": "$2b$12$abcd1234",  # Senha placeholder
            "tipo": "instrutor",
            "unidade_id": None,  # Será atualizado
            "curso_id": None,  # Será atualizado
            "ativo": True,
            "created_at": datetime.now(timezone.utc)
        }
        await db.usuarios.insert_one(jose_marcos)
        print(f"   ✅ Instrutor criado (ID: {jose_marcos['id']})")
    
    if "Instrutora Graziela" in missing:
        print("\n👩‍🏫 Criando instrutora Graziela...")
        graziela = {
            "id": str(uuid.uuid4()),
            "nome": "Graziela Dionísio dos Santos",
            "email": "graziela.santos@ios.org.br",
            "senha": "$2b$12$abcd1234",
            "tipo": "instrutor",
            "unidade_id": None,
            "curso_id": None,
            "ativo": True,
            "created_at": datetime.now(timezone.utc)
        }
        await db.usuarios.insert_one(graziela)
        print(f"   ✅ Instrutora criada (ID: {graziela['id']})")
    
    if "Instrutora Lise" in missing:
        print("\n👩‍🏫 Criando instrutora Lise...")
        lise = {
            "id": str(uuid.uuid4()),
            "nome": "Lise Hevellin Fliess Chaves",
            "email": "lise.chaves@ios.org.br",
            "senha": "$2b$12$abcd1234",
            "tipo": "instrutor",
            "unidade_id": None,
            "curso_id": None,
            "ativo": True,
            "created_at": datetime.now(timezone.utc)
        }
        await db.usuarios.insert_one(lise)
        print(f"   ✅ Instrutora criada (ID: {lise['id']})")
    
    if "Instrutor Ermerson" in missing:
        print("\n👨‍🏫 Criando instrutor Ermerson...")
        ermerson = {
            "id": str(uuid.uuid4()),
            "nome": "Ermeson da Silva Barros",
            "email": "ermerson.barros@ios.org.br",
            "senha": "$2b$12$abcd1234",
            "tipo": "instrutor",
            "unidade_id": None,
            "curso_id": None,
            "ativo": True,
            "created_at": datetime.now(timezone.utc)
        }
        await db.usuarios.insert_one(ermerson)
        print(f"   ✅ Instrutor criado (ID: {ermerson['id']})")

if __name__ == "__main__":
    asyncio.run(create_turmas())
