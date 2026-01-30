from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, UploadFile, File, Query, Form
from fastapi.responses import Response, StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
from enum import Enum
import uuid
from datetime import datetime, timezone, timedelta, date
import jwt
from passlib.hash import bcrypt
import base64
import csv
import re
from io import StringIO, BytesIO
from collections import defaultdict
import asyncio
from urllib.parse import quote_plus
from dateutil import parser as dateutil_parser
from pymongo.errors import DuplicateKeyError
from bson import ObjectId

# Carregamento de variáveis de ambiente
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# -------------------------
# Criação do FastAPI app
# -------------------------
app = FastAPI(title="Sistema de Controle de Presença - IOS")

# Middleware CORS - configurado para desenvolvimento e produção
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://sistema-ios-chamada.vercel.app",  # 🎯 URL específica do Vercel
    "https://front-end-sistema-qbl0lhxig-jesielamarojunior-makers-projects.vercel.app",
    "https://front-end-sistema.vercel.app",
    "https://sistema-ios-frontend.vercel.app",
    "https://sistema-ios-backend.onrender.com",  # 🚀 URL do próprio backend Render
    "*"  # 🚨 EMERGENCY: Permitir todas as origens para resolver CORS
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# 🚀 CORS EMERGENCY FIX - VERSÃO ROBUSTA
@app.middleware("http")
async def cors_handler(request, call_next):
    """Middleware CORS super robusto para resolver problemas de produção"""
    
    # Headers CORS mais permissivos
    cors_headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "*",
        "Access-Control-Allow-Headers": "*",
        "Access-Control-Allow-Credentials": "false",  # False quando origin é *
        "Access-Control-Max-Age": "86400",
        "Access-Control-Expose-Headers": "*"
    }
    
    # 🚨 PREFLIGHT - Resposta direta para OPTIONS
    if request.method == "OPTIONS":
        print(f"🔧 Handling PREFLIGHT for: {request.url}")
        response = Response(status_code=200, content="OK")
        for key, value in cors_headers.items():
            response.headers[key] = value
        return response
    
    try:
        # Processar requisição normal
        print(f"🔍 Processing {request.method} {request.url}")
        response = await call_next(request)
        
        # 🛡️ Força headers CORS em TODAS as respostas
        for key, value in cors_headers.items():
            response.headers[key] = value
            
        print(f"✅ CORS headers added to response: {response.status_code}")
        return response
        
    except Exception as e:
        # 🚨 ERRO: Ainda retorna resposta com CORS
        print(f"❌ Erro no middleware: {e}")
        error_response = Response(
            status_code=500, 
            content=f"Server Error: {str(e)}",
            media_type="text/plain"
        )
        for key, value in cors_headers.items():
            error_response.headers[key] = value
        return error_response

# Log da configuração CORS para debug
print(f"🔧 CORS configurado para origins: {origins}")
print(f"🌍 Ambiente: RENDER={os.environ.get('RENDER')}, RAILWAY={os.environ.get('RAILWAY_ENVIRONMENT')}")

# -------------------------
# MongoDB connection
# -------------------------
username = quote_plus("jesielamarojunior_db_user")
password = quote_plus("admin123")

MONGO_URL = f"mongodb+srv://{username}:{password}@cluster0.vuho6l7.mongodb.net/IOS-SISTEMA-CHAMADA?retryWrites=true&w=majority"
DB_NAME = "IOS-SISTEMA-CHAMADA"

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# 📁 GridFS para armazenamento de arquivos (atestados/justificativas)
fs_bucket = AsyncIOMotorGridFSBucket(db, bucket_name="justifications")

# -------------------------
# Teste de conexão MongoDB
# -------------------------
async def test_connection():
    try:
        await client.admin.command('ping')
        print("Conectado ao MongoDB Atlas ✅")
    except Exception as e:
        print("Erro ao conectar:", e)

# -------------------------
# Evento de startup
# -------------------------
@app.on_event("startup")
async def startup_event():
    await test_connection()
    # 🎯 PRODUÇÃO: Inicialização de dados de exemplo removida
    print("✅ Sistema iniciado SEM dados de exemplo")

# -------------------------
# Router e rota de teste
# -------------------------
api_router = APIRouter(prefix="/api")

@api_router.get("/ping")
async def ping():
    return {
        "message": "Backend funcionando!",
        "cors_origins": origins,
        "render_env": os.environ.get("RENDER"),
        "railway_env": os.environ.get("RAILWAY_ENVIRONMENT"),
        "timestamp": datetime.now().isoformat()
    }

@api_router.get("/cors-test")
async def cors_test():
    """Endpoint específico para testar CORS"""
    return {
        "status": "CORS working",
        "message": "Se você consegue ver esta mensagem, o CORS está funcionando!",
        "frontend_allowed": "https://sistema-ios-chamada.vercel.app",
        "all_origins": origins,
        "timestamp": datetime.now().isoformat()
    }

# -------------------------
# Configuração JWT
# -------------------------
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
security = HTTPBearer()

# Inclui o router no app (já criados acima)
app.include_router(api_router)

# CSV Format Enum for API
class CSVFormat(str, Enum):
    simple = "simple"
    complete = "complete"

# Enhanced Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    nome: str
    email: EmailStr
    senha: str
    tipo: str  # "admin", "instrutor", "pedagogo", "monitor"
    ativo: bool = True
    status: str = "ativo"  # "ativo", "pendente", "inativo"
    primeiro_acesso: bool = True
    token_confirmacao: Optional[str] = None
    unidade_id: Optional[str] = None  # Para instrutores/pedagogos/monitores
    curso_id: Optional[str] = None  # Para instrutores/pedagogos/monitores - curso específico
    telefone: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_login: Optional[datetime] = None

class UserCreate(BaseModel):
    nome: str
    email: EmailStr
    tipo: str
    unidade_id: Optional[str] = None
    curso_id: Optional[str] = None  # Obrigatório para instrutores/pedagogos/monitores
    telefone: Optional[str] = None

class UserUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None
    ativo: Optional[bool] = None
    unidade_id: Optional[str] = None
    curso_id: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    senha: str

class UserResponse(BaseModel):
    id: str
    nome: str
    email: str
    tipo: str
    ativo: bool
    unidade_id: Optional[str] = None
    curso_id: Optional[str] = None
    unidade_nome: Optional[str] = None
    curso_nome: Optional[str] = None

class FirstAccessRequest(BaseModel):
    nome: str
    email: EmailStr
    tipo: str
    status: str
    primeiro_acesso: bool
    unidade_id: Optional[str] = None
    curso_id: Optional[str] = None
    telefone: Optional[str] = None
    last_login: Optional[datetime] = None

class PasswordReset(BaseModel):
    senha_atual: str
    nova_senha: str

class Unidade(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    nome: str
    endereco: str
    telefone: Optional[str] = None
    responsavel: Optional[str] = None
    email: Optional[str] = None
    ativo: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UnidadeCreate(BaseModel):
    nome: str
    endereco: str
    telefone: Optional[str] = None
    responsavel: Optional[str] = None
    email: Optional[str] = None

class UnidadeUpdate(BaseModel):
    nome: Optional[str] = None
    endereco: Optional[str] = None
    telefone: Optional[str] = None
    responsavel: Optional[str] = None
    email: Optional[str] = None

class Curso(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    nome: str
    descricao: Optional[str] = None
    carga_horaria: int
    categoria: Optional[str] = None
    pre_requisitos: Optional[str] = None
    dias_aula: List[str] = ["segunda", "terca", "quarta", "quinta"]  # 📅 Dias de aula padrão
    ativo: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CursoCreate(BaseModel):
    nome: str
    descricao: Optional[str] = None
    carga_horaria: int
    categoria: Optional[str] = None
    pre_requisitos: Optional[str] = None
    dias_aula: List[str] = ["segunda", "terca", "quarta", "quinta"]  # 📅 Dias de aula

class CursoUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    carga_horaria: Optional[int] = None
    categoria: Optional[str] = None
    pre_requisitos: Optional[str] = None
    dias_aula: Optional[List[str]] = None  # 📅 Dias de aula

class Aluno(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    nome: str  # OBRIGATÓRIO - Nome completo
    cpf: str   # OBRIGATÓRIO - CPF válido
    data_nascimento: Optional[date] = None  # OPCIONAL para compatibilidade com dados existentes
    rg: Optional[str] = None
    genero: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    endereco: Optional[str] = None
    nome_responsavel: Optional[str] = None
    telefone_responsavel: Optional[str] = None
    observacoes: Optional[str] = None
    ativo: bool = True
    status: str = "ativo"  # "ativo", "desistente", "concluido", "suspenso"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AlunoCreate(BaseModel):
    nome: str  # OBRIGATÓRIO - Nome completo
    cpf: str   # OBRIGATÓRIO - CPF válido
    data_nascimento: date  # OBRIGATÓRIO - Data de nascimento
    rg: Optional[str] = None
    genero: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    endereco: Optional[str] = None
    nome_responsavel: Optional[str] = None
    telefone_responsavel: Optional[str] = None
    observacoes: Optional[str] = None

class AlunoUpdate(BaseModel):
    nome: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    endereco: Optional[str] = None
    nome_responsavel: Optional[str] = None
    telefone_responsavel: Optional[str] = None
    observacoes: Optional[str] = None
    status: Optional[str] = None

class Turma(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    nome: str
    unidade_id: str
    curso_id: str
    instrutor_id: str
    pedagogo_id: Optional[str] = None
    monitor_id: Optional[str] = None
    alunos_ids: List[str] = []
    data_inicio: date
    data_fim: date
    horario_inicio: str  # "08:00"
    horario_fim: str     # "17:00"
    dias_semana: List[str] = []  # ["segunda", "terca", "quarta", "quinta", "sexta"]
    vagas_total: int = 30
    vagas_ocupadas: int = 0
    ciclo: Optional[str] = None  # "01/2025", "02/2025" - Opcional para compatibilidade
    tipo_turma: str = "regular"  # "regular" (instrutor) ou "extensao" (pedagogo)
    ativo: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class TurmaCreate(BaseModel):
    nome: str
    unidade_id: str
    curso_id: str
    instrutor_id: str
    pedagogo_id: Optional[str] = None
    monitor_id: Optional[str] = None
    data_inicio: date
    data_fim: date
    horario_inicio: str
    horario_fim: str
    dias_semana: List[str]
    vagas_total: int = 30
    ciclo: Optional[str] = None
    tipo_turma: str = "regular"  # "regular" (instrutor) ou "extensao" (pedagogo)

class TurmaUpdate(BaseModel):
    nome: Optional[str] = None
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None
    horario_inicio: Optional[str] = None
    horario_fim: Optional[str] = None
    dias_semana: Optional[List[str]] = None
    tipo_turma: Optional[str] = None  # "regular" ou "extensao"
    vagas_total: Optional[int] = None
    instrutor_id: Optional[str] = None  # Permitir mudança de instrutor/responsável

class Chamada(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    turma_id: str
    instrutor_id: str
    data: date
    horario: str
    observacoes_aula: Optional[str] = None
    presencas: Dict[str, Dict[str, Any]]  # aluno_id -> {presente: bool, justificativa: str, atestado_id: str}
    total_presentes: int = 0
    total_faltas: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ChamadaCreate(BaseModel):
    turma_id: str
    data: date
    horario: str
    observacoes_aula: Optional[str] = None
    presencas: Dict[str, Dict[str, Any]]

class Desistente(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    aluno_id: str
    aluno_nome: Optional[str] = None  # Nome do aluno para facilitar exibição
    turma_id: Optional[str] = None  # Tornar opcional para permitir desistência sem turma específica
    data_desistencia: date
    motivo_codigo: str  # Código do motivo (ex: "nao_identificou")
    motivo_descricao: str  # Descrição legível do motivo
    motivo_personalizado: Optional[str] = None  # Texto personalizado se motivo for "outro"
    observacoes: Optional[str] = None
    registrado_por: str
    registrado_por_nome: Optional[str] = None  # Nome de quem registrou
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class DesistenteCreate(BaseModel):
    aluno_id: str
    turma_id: Optional[str] = None  # Tornar opcional para permitir desistência sem turma específica
    data_desistencia: date
    motivo_codigo: str  # Código do motivo
    motivo_descricao: str  # Descrição do motivo
    motivo_personalizado: Optional[str] = None  # Texto personalizado
    observacoes: Optional[str] = None

# 📋 MODELO PARA ATESTADOS
class AtestadoResponse(BaseModel):
    id: str
    aluno_id: str
    aluno_nome: str
    filename: str
    data_envio: date
    observacao: str
    uploaded_by_nome: str
    created_at: datetime

# 🚀 NOVOS MODELOS PARA SISTEMA DE ATTENDANCE (CHAMADAS PENDENTES)
class AttendanceRecord(BaseModel):
    aluno_id: str
    presente: bool
    nota: Optional[str] = None  # opcional: observações sobre o aluno

class AttendanceCreate(BaseModel):
    records: List[AttendanceRecord]
    observacao: Optional[str] = None  # observação geral da aula

class AttendanceResponse(BaseModel):
    id: str
    turma_id: str
    data: str  # YYYY-MM-DD
    created_by: str
    created_at: str
    records: List[AttendanceRecord]
    observacao: Optional[str] = None

class PendingAttendanceInfo(BaseModel):
    turma_id: str
    turma_nome: str
    data_pendente: str  # Data da chamada pendente (ISO format)
    dias_atras: int     # Quantos dias atrás (0=hoje, 1=ontem, etc.)
    prioridade: str     # "urgente", "importante", "pendente"
    status_msg: str     # Mensagem descritiva do status
    alunos: List[Dict[str, str]]  # [{"id": "...", "nome": "..."}]
    vagas: int
    horario: str

class PendingAttendancesResponse(BaseModel):
    date: str
    pending: List[PendingAttendanceInfo]

# 📋 SISTEMA DE JUSTIFICATIVAS/ATESTADOS - CÓDIGOS PADRONIZADOS
ALLOWED_REASON_CODES = {
    "NOT_IDENTIFIED_WITH_COURSE": "Não se identificou com o curso",
    "DIFFICULTY_FOLLOWING_COURSE": "Dificuldade para acompanhar o curso", 
    "OPTED_OTHER_COURSE": "Optou por outro curso",
    "NO_TRANSPORT_FUNDS": "Falta de recursos para transporte",
    "MOVED_ADDRESS": "Mudança de endereço",
    "NEEDS_TO_CARE_FOR_FAMILY": "Necessidade de cuidar da família",
    "NO_CONTACT_RETURN": "Não retornou contato",
    "HEALTH_PROBLEMS": "Problemas de saúde",
    "GOT_A_JOB": "Conseguiu emprego",
    "PREGNANCY_OR_LACTATION": "Gravidez ou lactação",
    "CUSTOM": "Outro motivo (especificar)"
}

# 📋 MODELOS PARA SISTEMA DE JUSTIFICATIVAS/ATESTADOS
class Justification(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    attendance_id: Optional[str] = None  # Vincula à chamada específica (opcional)
    uploaded_by: str  # ID do usuário que enviou
    uploaded_by_name: str  # Nome do usuário que enviou
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    reason_code: str  # Código padronizado do motivo
    reason_text: Optional[str] = None  # Descrição livre (obrigatória se reason_code = CUSTOM)
    file_id: Optional[str] = None  # GridFS file ID
    file_name: Optional[str] = None
    file_mime: Optional[str] = None
    file_size: Optional[int] = None
    status: str = "registered"  # "registered", "reviewed", "rejected"
    visible_to_student: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class JustificationCreate(BaseModel):
    student_id: str
    attendance_id: Optional[str] = None
    reason_code: str
    reason_text: Optional[str] = None

class JustificationResponse(BaseModel):
    id: str
    student_id: str
    attendance_id: Optional[str] = None
    uploaded_by: str
    uploaded_by_name: str
    uploaded_at: datetime
    reason_code: str
    reason_text: Optional[str] = None
    file_name: Optional[str] = None
    file_mime: Optional[str] = None
    file_size: Optional[int] = None
    status: str
    visible_to_student: bool
    has_file: bool = False  # Computed field

# Helper Functions
def prepare_for_mongo(data):
    """Convert date objects to ISO strings for MongoDB storage"""
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, date):
                data[key] = value.isoformat()
            elif isinstance(value, datetime):
                data[key] = value.isoformat()
    return data

def parse_from_mongo(item):
    """Parse ISO strings back to date objects from MongoDB"""
    if isinstance(item, dict):
        # Remove MongoDB ObjectId field if present
        if '_id' in item:
            del item['_id']
            
        for key, value in item.items():
            if isinstance(value, str) and key in ['data_inicio', 'data_fim', 'data', 'data_nascimento', 'data_desistencia']:
                try:
                    item[key] = datetime.fromisoformat(value).date()
                except (ValueError, AttributeError):
                    pass
    return item

# 🚀 NOVA FUNÇÃO HELPER PARA ATTENDANCE
def today_iso_date(tz=None):
    """Retorna data ISO YYYY-MM-DD (use timezone UTC ou local se desejar)"""
    return datetime.now(timezone.utc).date().isoformat()

# Bulk Upload Helper Functions
def normalize_cpf(raw: str) -> str:
    """Remove all non-digit characters from CPF"""
    if raw is None:
        return ""
    s = re.sub(r"\D", "", str(raw))
    return s

def validate_cpf(cpf: str) -> bool:
    """Validate Brazilian CPF number"""
    cpf = normalize_cpf(cpf)
    if len(cpf) != 11:
        return False
    # evita sequências iguais
    if cpf == cpf[0] * 11:
        return False

    def calc_digit(cpf_slice: str) -> int:
        size = len(cpf_slice) + 1
        total = 0
        for i, ch in enumerate(cpf_slice):
            total += int(ch) * (size - i)
        r = total % 11
        return 0 if r < 2 else 11 - r

    d1 = calc_digit(cpf[:9])
    d2 = calc_digit(cpf[:10])
    return d1 == int(cpf[9]) and d2 == int(cpf[10])

def parse_date_str(s: str) -> date:
    """Parse date string in various formats"""
    if s is None:
        raise ValueError("Data vazia")
    s = str(s).strip()
    # tenta formatos comuns
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(s, fmt).date()
        except Exception:
            pass
    # fallback mais flexível
    try:
        return dateutil_parser.parse(s, dayfirst=True).date()
    except Exception as e:
        raise ValueError("Formato de data inválido. Utilize YYYY-MM-DD ou DD/MM/YYYY") from e

# JWT Token Functions
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_email: str = payload.get("sub")
        if user_email is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        
        user = await db.usuarios.find_one({"email": user_email})
        if user is None:
            raise HTTPException(status_code=401, detail="Usuário não encontrado")
        
        return UserResponse(**user)
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

def check_admin_permission(current_user: UserResponse):
    if current_user.tipo != "admin":
        raise HTTPException(status_code=403, detail="Apenas administradores podem realizar esta ação")

# 🔒 PERMISSÕES RBAC PARA JUSTIFICATIVAS
async def user_can_manage_student(current_user: UserResponse, student_id: str) -> bool:
    """
    Verifica se o usuário pode gerenciar um aluno específico baseado em suas permissões:
    - Admin: pode gerenciar qualquer aluno
    - Instrutor: pode gerenciar alunos de suas turmas
    - Pedagogo: pode gerenciar alunos de sua unidade/curso
    - Monitor: pode gerenciar alunos das turmas que monitora
    """
    if current_user.tipo == "admin":
        return True
    
    if current_user.tipo == "instrutor":
        # Verificar se aluno está em alguma turma do instrutor
        turmas_instrutor = await db.turmas.find({"instrutor_id": current_user.id}).to_list(1000)
        for turma in turmas_instrutor:
            if student_id in turma.get("alunos_ids", []):
                return True
        return False
    
    if current_user.tipo == "pedagogo":
        # Verificar se aluno pertence à unidade/curso do pedagogo
        # Primeiro buscar turmas da unidade/curso do pedagogo
        query = {}
        if getattr(current_user, 'unidade_id', None):
            query["unidade_id"] = getattr(current_user, 'unidade_id', None)
        if getattr(current_user, 'curso_id', None):
            query["curso_id"] = getattr(current_user, 'curso_id', None)
            
        turmas_pedagogo = await db.turmas.find(query).to_list(1000)
        for turma in turmas_pedagogo:
            if student_id in turma.get("alunos_ids", []):
                return True
        return False
    
    if current_user.tipo == "monitor":
        # Verificar se aluno está em turmas que o monitor acompanha
        turmas_monitor = await db.turmas.find({"monitor_id": current_user.id}).to_list(1000)
        for turma in turmas_monitor:
            if student_id in turma.get("alunos_ids", []):
                return True
        return False
    
    return False

# AUTH ROUTES
@api_router.post("/auth/login")
async def login(user_login: UserLogin):
    user = await db.usuarios.find_one({"email": user_login.email})
    if not user or not bcrypt.verify(user_login.senha, user["senha"]):
        raise HTTPException(status_code=401, detail="Email ou senha incorretos")
    
    if not user["ativo"]:
        raise HTTPException(status_code=401, detail="Usuário inativo")
    
    if user.get("status") == "pendente":
        raise HTTPException(status_code=401, detail="Usuário aguardando aprovação do administrador")
    
    # Update last login
    await db.usuarios.update_one(
        {"id": user["id"]},
        {"$set": {"last_login": datetime.now(timezone.utc)}}
    )
    
    access_token = create_access_token(data={"sub": user["email"], "tipo": user["tipo"]})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse(**user)
    }

@api_router.post("/auth/first-access")
async def first_access_request(user_data: FirstAccessRequest):
    print(f"🔍 Recebida solicitação de primeiro acesso: {user_data.email} - {user_data.tipo}")
    
    # Check if user already exists
    existing_user = await db.usuarios.find_one({"email": user_data.email})
    if existing_user:
        print(f"❌ Email já cadastrado: {user_data.email}")
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    
    # Generate temporary password
    temp_password = str(uuid.uuid4())[:8]
    hashed_password = bcrypt.hash(temp_password)
    
    print(f"✅ Criando usuário pendente: {user_data.nome}")
    
    user_obj = User(
        nome=user_data.nome,
        email=user_data.email,
        senha=hashed_password,
        tipo=user_data.tipo,
        status="pendente",
        primeiro_acesso=True
    )
    
    await db.usuarios.insert_one(user_obj.dict())
    
    print(f"✅ Usuário criado com sucesso: {user_data.email}")
    return {"message": "Solicitação de acesso enviada com sucesso", "temp_password": temp_password}

@api_router.get("/auth/me", response_model=UserResponse)
async def get_me(current_user: UserResponse = Depends(get_current_user)):
    return current_user

@api_router.post("/auth/change-password")
async def change_password(password_reset: PasswordReset, current_user: UserResponse = Depends(get_current_user)):
    user = await db.usuarios.find_one({"id": current_user.id})
    if not bcrypt.verify(password_reset.senha_atual, user["senha"]):
        raise HTTPException(status_code=400, detail="Senha atual incorreta")
    
    hashed_password = bcrypt.hash(password_reset.nova_senha)
    await db.usuarios.update_one(
        {"id": current_user.id},
        {"$set": {"senha": hashed_password, "primeiro_acesso": False}}
    )
    
    return {"message": "Senha alterada com sucesso"}

# USER MANAGEMENT ROUTES
@api_router.post("/users", response_model=UserResponse)
async def create_user(user_create: UserCreate, current_user: UserResponse = Depends(get_current_user)):
    check_admin_permission(current_user)
    
    # Check if user already exists
    existing_user = await db.usuarios.find_one({"email": user_create.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    
    # Validação específica para instrutores, pedagogos e monitores
    if user_create.tipo in ["instrutor", "pedagogo", "monitor"]:
        if not user_create.unidade_id:
            raise HTTPException(status_code=400, detail="Unidade é obrigatória para instrutores, pedagogos e monitores")
        
        if not user_create.curso_id:
            raise HTTPException(status_code=400, detail="Curso é obrigatório para instrutores, pedagogos e monitores")
        
        # Verificar se unidade existe
        unidade = await db.unidades.find_one({"id": user_create.unidade_id})
        if not unidade:
            raise HTTPException(status_code=400, detail="Unidade não encontrada")
        
        # Verificar se curso existe
        curso = await db.cursos.find_one({"id": user_create.curso_id})
        if not curso:
            raise HTTPException(status_code=400, detail="Curso não encontrado")
    
    # Generate temporary password and confirmation token
    temp_password = str(uuid.uuid4())[:8]
    hashed_password = bcrypt.hash(temp_password)
    confirmation_token = str(uuid.uuid4())
    
    user_dict = user_create.dict()
    user_dict.update({
        "senha": hashed_password,
        "status": "pendente",
        "primeiro_acesso": True,
        "token_confirmacao": confirmation_token
    })
    
    user_obj = User(**user_dict)
    await db.usuarios.insert_one(user_obj.dict())
    
    # Log da criação para auditoria (removido temporariamente - função não implementada)
    # TODO: Implement log_admin_action function for audit trail
    print(f"👤 Admin {current_user.email} criou usuário {user_create.tipo}: {user_create.nome} ({user_create.email})")
    
    response = UserResponse(**user_obj.dict())
    return response

@api_router.get("/users", response_model=List[UserResponse])
async def get_users(
    skip: int = 0, 
    limit: int = 100,
    tipo: Optional[str] = None,
    status: Optional[str] = None,
    current_user: UserResponse = Depends(get_current_user)
):
    # Admin can see all users, others can see basic user info
    if current_user.tipo != "admin" and current_user.tipo not in ["instrutor", "pedagogo"]:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    query = {}
    if tipo:
        query["tipo"] = tipo
    if status:
        query["status"] = status
        
    users = await db.usuarios.find(query).skip(skip).limit(limit).to_list(limit)
    
    # Enriquecer dados com nomes de unidade e curso
    result_users = []
    for user in users:
        user_response = UserResponse(**user)
        
        # Buscar nome da unidade
        if user.get('unidade_id'):
            unidade = await db.unidades.find_one({"id": user.get('unidade_id')})
            if unidade:
                user_response.unidade_nome = unidade.get('nome')
        
        # Buscar nome do curso
        if user.get('curso_id'):
            curso = await db.cursos.find_one({"id": user.get('curso_id')})
            if curso:
                user_response.curso_nome = curso.get('nome')
        
        result_users.append(user_response)
    
    return result_users

@api_router.get("/users/pending", response_model=List[UserResponse])
async def get_pending_users(current_user: UserResponse = Depends(get_current_user)):
    check_admin_permission(current_user)
    
    users = await db.usuarios.find({"status": "pendente"}).to_list(100)
    return [UserResponse(**user) for user in users]

@api_router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_by_id(user_id: str, current_user: UserResponse = Depends(get_current_user)):
    check_admin_permission(current_user)
    
    user = await db.usuarios.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    user_response = UserResponse(**user)
    
    # Buscar nome da unidade
    if user.get('unidade_id'):
        unidade = await db.unidades.find_one({"id": user.get('unidade_id')})
        if unidade:
            user_response.unidade_nome = unidade.get('nome')
    
    # Buscar nome do curso
    if user.get('curso_id'):
        curso = await db.cursos.find_one({"id": user.get('curso_id')})
        if curso:
            user_response.curso_nome = curso.get('nome')
    
    return user_response

@api_router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, user_update: UserUpdate, current_user: UserResponse = Depends(get_current_user)):
    check_admin_permission(current_user)
    
    update_data = {k: v for k, v in user_update.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="Nenhum dado para atualizar")
    
    result = await db.usuarios.update_one({"id": user_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    updated_user = await db.usuarios.find_one({"id": user_id})
    return UserResponse(**updated_user)

@api_router.post("/auth/reset-password-request")
async def reset_password_request(email_data: dict):
    """
    Reset de senha para usuário comum
    🔐 SEGURANÇA: Não expõe se email existe ou não
    📧 TODO: Implementar envio por email
    """
    email = email_data.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email é obrigatório")
    
    # Check if user exists
    user = await db.usuarios.find_one({"email": email})
    
    if user:
        # Generate new temporary password
        temp_password = str(uuid.uuid4())[:8]
        hashed_password = bcrypt.hash(temp_password)
        
        # Update user password
        await db.usuarios.update_one(
            {"email": email},
            {"$set": {"senha": hashed_password, "primeiro_acesso": True}}
        )
        
        # TODO: Enviar por email
        # send_password_email(email, temp_password)
        print(f"🔐 SENHA TEMPORÁRIA PARA {email}: {temp_password}")
    
    # ✅ SEGURANÇA: Sempre retorna sucesso (não expõe se email existe)
    return {"message": "Se o email estiver cadastrado, uma nova senha será enviada"}

@api_router.post("/users/{user_id}/reset-password")
async def admin_reset_user_password(user_id: str, current_user: UserResponse = Depends(get_current_user)):
    """
    Reset de senha administrativo
    👨‍💼 ADMIN: Pode resetar senha de qualquer usuário
    🔐 SEGURANÇA: Retorna senha para admin informar pessoalmente
    """
    check_admin_permission(current_user)
    
    # Buscar dados do usuário
    user = await db.usuarios.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Generate new temporary password
    temp_password = str(uuid.uuid4())[:8]
    hashed_password = bcrypt.hash(temp_password)
    
    # Update user password
    result = await db.usuarios.update_one(
        {"id": user_id},
        {"$set": {"senha": hashed_password, "primeiro_acesso": True}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Erro ao atualizar senha")
    
    # Log da ação administrativa
    print(f"🔐 ADMIN {current_user.email} resetou senha de {user['email']}: {temp_password}")
    
    return {
        "message": "Senha resetada com sucesso", 
        "temp_password": temp_password,
        "user_email": user["email"],
        "user_name": user["nome"]
    }

@api_router.put("/users/{user_id}/approve")
async def approve_user(user_id: str, current_user: UserResponse = Depends(get_current_user)):
    check_admin_permission(current_user)
    
    # Generate a new temporary password for the approved user
    temp_password = str(uuid.uuid4())[:8]
    hashed_password = bcrypt.hash(temp_password)
    
    result = await db.usuarios.update_one(
        {"id": user_id}, 
        {"$set": {"status": "ativo", "senha": hashed_password}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    return {"message": "Usuário aprovado com sucesso", "temp_password": temp_password}

@api_router.delete("/users/{user_id}")
async def delete_user(user_id: str, current_user: UserResponse = Depends(get_current_user)):
    check_admin_permission(current_user)
    
    result = await db.usuarios.update_one({"id": user_id}, {"$set": {"ativo": False}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    return {"message": "Usuário desativado com sucesso"}

# UNIDADES ROUTES
@api_router.post("/units", response_model=Unidade)
async def create_unidade(unidade_create: UnidadeCreate, current_user: UserResponse = Depends(get_current_user)):
    check_admin_permission(current_user)
    
    unidade_obj = Unidade(**unidade_create.dict())
    await db.unidades.insert_one(unidade_obj.dict())
    return unidade_obj

@api_router.get("/units", response_model=List[Unidade])
async def get_unidades(current_user: UserResponse = Depends(get_current_user)):
    unidades = await db.unidades.find({"ativo": True}).to_list(1000)
    return [Unidade(**unidade) for unidade in unidades]

@api_router.put("/units/{unidade_id}", response_model=Unidade)
async def update_unidade(unidade_id: str, unidade_update: UnidadeUpdate, current_user: UserResponse = Depends(get_current_user)):
    check_admin_permission(current_user)
    
    update_data = {k: v for k, v in unidade_update.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="Nenhum dado para atualizar")
    
    result = await db.unidades.update_one({"id": unidade_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Unidade não encontrada")
    
    updated_unidade = await db.unidades.find_one({"id": unidade_id})
    return Unidade(**updated_unidade)

@api_router.delete("/units/{unidade_id}")
async def delete_unidade(unidade_id: str, current_user: UserResponse = Depends(get_current_user)):
    check_admin_permission(current_user)
    
    result = await db.unidades.update_one({"id": unidade_id}, {"$set": {"ativo": False}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Unidade não encontrada")
    
    return {"message": "Unidade desativada com sucesso"}

# CURSOS ROUTES
@api_router.post("/courses", response_model=Curso)
async def create_curso(curso_create: CursoCreate, current_user: UserResponse = Depends(get_current_user)):
    check_admin_permission(current_user)
    
    curso_obj = Curso(**curso_create.dict())
    await db.cursos.insert_one(curso_obj.dict())
    return curso_obj

@api_router.get("/courses", response_model=List[Curso])
async def get_cursos(current_user: UserResponse = Depends(get_current_user)):
    cursos = await db.cursos.find({"ativo": True}).to_list(1000)
    return [Curso(**curso) for curso in cursos]

@api_router.get("/users/{user_id}/details")
async def get_user_details(user_id: str, current_user: UserResponse = Depends(get_current_user)):
    # Admin pode ver detalhes de qualquer usuário
    if current_user.tipo != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    user = await db.usuarios.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    user_response = UserResponse(**user)
    details = {"user": user_response}
    
    # Buscar informações da unidade
    if user.get("unidade_id"):
        unidade = await db.unidades.find_one({"id": user["unidade_id"]})
        details["unidade"] = unidade
    
    # Buscar informações do curso
    if user.get("curso_id"):
        curso = await db.cursos.find_one({"id": user["curso_id"]})
        details["curso"] = curso
    
    return details

@api_router.put("/courses/{curso_id}", response_model=Curso)
async def update_curso(curso_id: str, curso_update: CursoUpdate, current_user: UserResponse = Depends(get_current_user)):
    check_admin_permission(current_user)
    
    update_data = {k: v for k, v in curso_update.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="Nenhum dado para atualizar")
    
    result = await db.cursos.update_one({"id": curso_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Curso não encontrado")
    
    updated_curso = await db.cursos.find_one({"id": curso_id})
    return Curso(**updated_curso)

@api_router.delete("/courses/{curso_id}")
async def delete_curso(curso_id: str, current_user: UserResponse = Depends(get_current_user)):
    check_admin_permission(current_user)
    
    result = await db.cursos.update_one({"id": curso_id}, {"$set": {"ativo": False}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Curso não encontrado")
    
    return {"message": "Curso desativado com sucesso"}

# ALUNOS ROUTES
@api_router.post("/students", response_model=Aluno)
async def create_aluno(aluno_create: AlunoCreate, current_user: UserResponse = Depends(get_current_user)):
    """📖 CADASTRO DE ALUNO - LÓGICA REFINADA 29/09/2025
    
    👨‍🏫 Instrutor: Cadastra apenas no seu curso
    📊 Pedagogo: Cadastra em qualquer curso da sua unidade  
    👩‍💻 Monitor: NÃO pode cadastrar alunos
    👑 Admin: Cadastra em qualquer lugar
    """
    
    # 🔒 MONITOR: Não pode cadastrar alunos
    if current_user.tipo == "monitor":
        raise HTTPException(
            status_code=403, 
            detail="Monitores não podem cadastrar alunos. Apenas visualizar."
        )
    
    # 👑 ADMIN: Pode cadastrar qualquer aluno
    if current_user.tipo == "admin":
        print(f"👑 Admin {current_user.email} cadastrando aluno: {aluno_create.nome}")
        
    # 👨‍🏫 INSTRUTOR: Apenas no seu curso específico
    elif current_user.tipo == "instrutor":
        if not getattr(current_user, 'curso_id', None) or not getattr(current_user, 'unidade_id', None):
            raise HTTPException(
                status_code=403, 
                detail="Instrutor deve ter curso e unidade atribuídos"
            )
        
        # Aluno será automaticamente vinculado ao curso do instrutor
        print(f"👨‍🏫 Instrutor {current_user.email} cadastrando aluno no curso {getattr(current_user, 'curso_id', None)}")
        
    # 📊 PEDAGOGO: Qualquer curso da sua unidade
    elif current_user.tipo == "pedagogo":
        if not getattr(current_user, 'unidade_id', None):
            raise HTTPException(
                status_code=403, 
                detail="Pedagogo deve ter unidade atribuída"
            )
        
        # Pedagogo pode escolher curso da unidade dele (validado no frontend)
        print(f"📊 Pedagogo {current_user.email} cadastrando aluno na unidade {getattr(current_user, 'unidade_id', None)}")
        
    else:
        raise HTTPException(status_code=403, detail="Tipo de usuário não autorizado para cadastrar alunos")
    
    # ✅ VALIDAÇÃO: CPF único no sistema
    existing_aluno = await db.alunos.find_one({"cpf": aluno_create.cpf})
    if existing_aluno:
        raise HTTPException(status_code=400, detail="CPF já cadastrado no sistema")
    
    # ✅ VALIDAÇÃO: Nome completo obrigatório (não aceita "Aluno 1", "Aluno 2")
    if len(aluno_create.nome.strip()) < 3 or aluno_create.nome.strip().lower().startswith("aluno"):
        raise HTTPException(
            status_code=400, 
            detail="Nome completo é obrigatório. Não é permitido 'Aluno 1', 'Aluno 2', etc."
        )
    
    aluno_dict = prepare_for_mongo(aluno_create.dict())
    aluno_obj = Aluno(**aluno_dict)
    
    # ✅ REGISTRAR QUEM CRIOU O ALUNO
    mongo_data = prepare_for_mongo(aluno_obj.dict())
    mongo_data["created_by"] = current_user.id  # ID do usuário que criou
    mongo_data["created_by_name"] = current_user.nome  # Nome do usuário que criou
    mongo_data["created_by_type"] = current_user.tipo  # Tipo do usuário que criou
    
    print(f"🔍 Criando aluno '{aluno_create.nome}' por {current_user.nome} (ID: {current_user.id})")
    print(f"   created_by: {mongo_data['created_by']}")
    print(f"   created_by_name: {mongo_data['created_by_name']}")
    
    await db.alunos.insert_one(mongo_data)
    
    return aluno_obj

@api_router.get("/students", response_model=List[Aluno])
async def get_alunos(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    current_user: UserResponse = Depends(get_current_user)
):
    """🎯 LISTAGEM DE ALUNOS: Filtrada por permissões do usuário"""
    
    print(f"🔍 Buscando alunos para usuário: {current_user.email} (tipo: {current_user.tipo})")
    print(f"   Curso ID: {getattr(current_user, 'curso_id', None)}")
    print(f"   Unidade ID: {getattr(current_user, 'unidade_id', None)}")
    
    # 👁️ FILTROS POR TIPO DE USUÁRIO - LÓGICA DETALHADA 29/09/2025
    if current_user.tipo == "admin":
        # 👑 Admin: vê TODOS os alunos (inclusive inativos para debug)
        print("👑 Admin visualizando todos os alunos (ativos e inativos)")
        query = {}
        if status:
            query["status"] = status
    elif current_user.tipo == "instrutor":
        # 👨‍🏫 INSTRUTOR: VÊ APENAS ALUNOS DAS TURMAS QUE ELE LECIONA
        # NOVA LÓGICA: Similar ao pedagogo, mas filtrado por curso específico do instrutor
        
        if not getattr(current_user, 'curso_id', None) or not getattr(current_user, 'unidade_id', None):
            print("❌ Instrutor sem curso ou unidade definida")
            return []
            
        # Buscar todas as turmas do curso específico do instrutor na sua unidade
        turmas_instrutor = await db.turmas.find({
            "curso_id": getattr(current_user, 'curso_id', None),
            "unidade_id": getattr(current_user, 'unidade_id', None),
            "instrutor_id": current_user.id,  # Apenas turmas que ele leciona
            "ativo": True
        }).to_list(1000)
        
        print(f"🔍 Instrutor {current_user.email} leciona {len(turmas_instrutor)} turmas")
        
        # Coletar IDs de todos os alunos das turmas do instrutor
        aluno_ids = set()
        for turma in turmas_instrutor:
            turma_alunos = turma.get("alunos_ids", [])
            aluno_ids.update(turma_alunos)
            print(f"   Turma '{turma['nome']}': {len(turma_alunos)} alunos")
        
        if aluno_ids:
            query = {"id": {"$in": list(aluno_ids)}, "ativo": True}
            print(f"👨‍🏫 Instrutor vendo {len(aluno_ids)} alunos das suas turmas")
        else:
            print("👨‍🏫 Instrutor: nenhum aluno nas turmas lecionadas")
            return []
            
    elif current_user.tipo == "pedagogo":
        # 📊 Pedagogo: vê todos os cursos da unidade
        if not getattr(current_user, 'unidade_id', None):
            print("❌ Pedagogo sem unidade definida")
            return []
            
        # Buscar todas as turmas da unidade
        turmas_unidade = await db.turmas.find({
            "unidade_id": getattr(current_user, 'unidade_id', None),
            "ativo": True
        }).to_list(1000)
        
        # Coletar IDs de todos os alunos da unidade
        aluno_ids = set()
        for turma in turmas_unidade:
            aluno_ids.update(turma.get("alunos_ids", []))
        
        if aluno_ids:
            query = {"id": {"$in": list(aluno_ids)}, "ativo": True}
            print(f"📊 Pedagogo vendo {len(aluno_ids)} alunos da unidade {getattr(current_user, 'unidade_id', None)}")
        else:
            print("📊 Pedagogo: nenhum aluno nas turmas da unidade")
            return []
            
    elif current_user.tipo == "monitor":
        # 👩‍💻 MONITOR: VÊ TODOS OS ALUNOS DA UNIDADE (igual ao pedagogo)
        if not getattr(current_user, 'unidade_id', None):
            print("❌ Monitor sem unidade definida")
            return []
            
        # Buscar todas as turmas da unidade (igual lógica do pedagogo)
        turmas_unidade = await db.turmas.find({
            "unidade_id": getattr(current_user, 'unidade_id', None),
            "ativo": True
        }).to_list(1000)
        
        print(f"🔍 Monitor {current_user.email} da unidade {getattr(current_user, 'unidade_id', None)}")
        print(f"   Turmas na unidade: {len(turmas_unidade)}")
        
        # Coletar IDs de todos os alunos da unidade
        aluno_ids = set()
        for turma in turmas_unidade:
            turma_alunos = turma.get("alunos_ids", [])
            aluno_ids.update(turma_alunos)
            nome_turma = turma.get("nome", "N/A")
            print(f"   Turma '{nome_turma}': {len(turma_alunos)} alunos")
        
        if aluno_ids:
            query = {"id": {"$in": list(aluno_ids)}, "ativo": True}
            print(f"👩‍💻 Monitor vendo {len(aluno_ids)} alunos da unidade")
        else:
            print("👩‍💻 Monitor: nenhum aluno nas turmas da unidade")
            return []
    else:
        # Outros tipos de usuário não podem ver alunos
        print(f"❌ Tipo de usuário {current_user.tipo} não autorizado")
        return []
        
    print(f"🔍 Query final para alunos: {query}")
    alunos = await db.alunos.find(query).skip(skip).limit(limit).to_list(limit)
    print(f"📊 Total de alunos encontrados: {len(alunos)}")
    
    # ✅ CORREÇÃO 422: Tratamento seguro de dados de alunos
    result_alunos = []
    for aluno in alunos:
        try:
            parsed_aluno = parse_from_mongo(aluno)
            # Garantir campos obrigatórios para compatibilidade
            if 'data_nascimento' not in parsed_aluno or parsed_aluno['data_nascimento'] is None:
                parsed_aluno['data_nascimento'] = None  # Garantir campo existe
            
            aluno_obj = Aluno(**parsed_aluno)
            result_alunos.append(aluno_obj)
        except Exception as e:
            # Log do erro mas não quebra a listagem
            print(f"⚠️ Erro ao processar aluno {aluno.get('id', 'SEM_ID')}: {e}")
            continue
    
    return result_alunos

@api_router.put("/students/{aluno_id}", response_model=Aluno)
async def update_aluno(aluno_id: str, aluno_update: AlunoUpdate, current_user: UserResponse = Depends(get_current_user)):
    check_admin_permission(current_user)
    
    update_data = {k: v for k, v in aluno_update.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="Nenhum dado para atualizar")
    
    result = await db.alunos.update_one({"id": aluno_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    
    updated_aluno = await db.alunos.find_one({"id": aluno_id})
    return Aluno(**parse_from_mongo(updated_aluno))

@api_router.post("/students/cleanup-orphans")
async def cleanup_orphan_students(current_user: UserResponse = Depends(get_current_user)):
    """🧹 LIMPEZA DE ALUNOS ÓRFÃOS - Remove alunos não vinculados a turmas
    
    🚨 APENAS ADMIN pode executar esta operação
    Remove alunos que não estão em nenhuma turma ativa
    """
    check_admin_permission(current_user)
    
    print(f"🧹 Iniciando limpeza de alunos órfãos por {current_user.email}")
    
    # Buscar todas as turmas ativas
    turmas_ativas = await db.turmas.find({"ativo": True}).to_list(10000)
    
    # Coletar todos os IDs de alunos que estão em turmas
    alunos_em_turmas = set()
    for turma in turmas_ativas:
        alunos_em_turmas.update(turma.get("alunos_ids", []))
    
    print(f"📊 {len(alunos_em_turmas)} alunos estão vinculados a turmas ativas")
    
    # Buscar alunos órfãos (não estão em alunos_em_turmas)
    query_orfaos = {
        "ativo": True,
        "id": {"$nin": list(alunos_em_turmas)}
    }
    
    alunos_orfaos = await db.alunos.find(query_orfaos).to_list(10000)
    print(f"🚨 {len(alunos_orfaos)} alunos órfãos encontrados")
    
    if not alunos_orfaos:
        return {
            "message": "Nenhum aluno órfão encontrado",
            "orphans_found": 0,
            "orphans_removed": 0
        }
    
    # Log dos alunos que serão removidos
    orphan_names = [aluno.get("nome", "SEM_NOME") for aluno in alunos_orfaos]
    print(f"📝 Alunos órfãos: {', '.join(orphan_names[:10])}{'...' if len(orphan_names) > 10 else ''}")
    
    # Marcar alunos órfãos como inativos (soft delete)
    orphan_ids = [aluno["id"] for aluno in alunos_orfaos]
    result = await db.alunos.update_many(
        {"id": {"$in": orphan_ids}},
        {"$set": {"ativo": False, "removed_reason": "orphan_cleanup", "removed_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    print(f"✅ {result.modified_count} alunos órfãos marcados como inativos")
    
    return {
        "message": f"Limpeza concluída: {result.modified_count} alunos órfãos removidos",
        "orphans_found": len(alunos_orfaos),
        "orphans_removed": result.modified_count,
        "orphan_names": orphan_names[:20]  # Máximo 20 nomes no retorno
    }

@api_router.post("/students/fix-created-by")
async def fix_alunos_created_by(current_user: UserResponse = Depends(get_current_user)):
    """🔧 MIGRAÇÃO: Corrigir alunos sem created_by associando aos instrutores das turmas
    
    Este endpoint resolve o problema de alunos antigos que não aparecem para instrutores
    porque foram criados antes da implementação do campo created_by.
    """
    
    # 🔒 VERIFICAÇÃO: Apenas admin pode executar migração
    if current_user.tipo != "admin":
        raise HTTPException(
            status_code=403, 
            detail="Apenas administradores podem executar migração de dados"
        )
    
    try:
        # 1. Buscar alunos sem created_by
        alunos_sem_created_by = await db.alunos.find({
            "$or": [
                {"created_by": {"$exists": False}},
                {"created_by": None},
                {"created_by": ""}
            ],
            "ativo": True
        }).to_list(1000)
        
        print(f"🔍 Encontrados {len(alunos_sem_created_by)} alunos sem created_by")
        
        if not alunos_sem_created_by:
            return {
                "message": "Nenhum aluno precisa de correção",
                "alunos_corrigidos": 0,
                "detalhes": []
            }
        
        # 2. Buscar todas as turmas ativas
        turmas = await db.turmas.find({"ativo": True}).to_list(1000)
        turmas_dict = {turma["id"]: turma for turma in turmas}
        
        # 3. Buscar instrutores para cada turma
        instrutores = await db.usuarios.find({
            "tipo": "instrutor",
            "status": "ativo"
        }).to_list(1000)
        instrutores_dict = {instrutor["id"]: instrutor for instrutor in instrutores}
        
        detalhes = []
        alunos_corrigidos = 0
        
        # 4. Para cada aluno sem created_by
        for aluno in alunos_sem_created_by:
            turma_id = aluno.get("turma_id")
            
            if turma_id and turma_id in turmas_dict:
                # Aluno está em uma turma - associar ao instrutor da turma
                turma = turmas_dict[turma_id]
                instrutor_id = turma.get("instrutor_id")
                
                if instrutor_id and instrutor_id in instrutores_dict:
                    instrutor = instrutores_dict[instrutor_id]
                    
                    # Atualizar aluno com dados do instrutor
                    await db.alunos.update_one(
                        {"id": aluno["id"]},
                        {
                            "$set": {
                                "created_by": instrutor_id,
                                "created_by_name": instrutor["nome"],
                                "created_by_type": "instrutor"
                            }
                        }
                    )
                    
                    alunos_corrigidos += 1
                    detalhes.append({
                        "aluno": aluno["nome"],
                        "cpf": aluno.get("cpf", "N/A"),
                        "turma": turma["nome"],
                        "instrutor": instrutor["nome"],
                        "acao": "associado_ao_instrutor_da_turma"
                    })
                    
                    print(f"✅ {aluno['nome']} → instrutor {instrutor['nome']} (turma {turma['nome']})")
                else:
                    detalhes.append({
                        "aluno": aluno["nome"],
                        "cpf": aluno.get("cpf", "N/A"),
                        "turma": turma["nome"],
                        "problema": "turma_sem_instrutor",
                        "acao": "nao_corrigido"
                    })
            else:
                # Aluno não está em turma - manter sem created_by (será removido na limpeza)
                detalhes.append({
                    "aluno": aluno["nome"],
                    "cpf": aluno.get("cpf", "N/A"),
                    "problema": "sem_turma",
                    "acao": "nao_corrigido"
                })
        
        return {
            "message": f"Migração concluída: {alunos_corrigidos} alunos associados a instrutores",
            "total_encontrados": len(alunos_sem_created_by),
            "alunos_corrigidos": alunos_corrigidos,
            "detalhes": detalhes[:50]  # Máximo 50 no retorno
        }
        
    except Exception as e:
        print(f"❌ Erro na migração: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno na migração: {str(e)}"
        )

@api_router.post("/database/reset-all")
async def reset_all_database(current_user: UserResponse = Depends(get_current_user)):
    """🚨 RESET TOTAL: Apaga TODOS os alunos e turmas do banco
    
    ⚠️ CUIDADO: Esta operação não pode ser desfeita!
    """
    
    # 🔒 VERIFICAÇÃO: Apenas admin pode executar
    if current_user.tipo != "admin":
        raise HTTPException(
            status_code=403, 
            detail="Apenas administradores podem resetar o banco"
        )
    
    try:
        # Contar antes da limpeza
        alunos_count = await db.alunos.count_documents({})
        turmas_count = await db.turmas.count_documents({})
        # 🎯 CORREÇÃO CRÍTICA: Usar collection 'attendances' (não 'chamadas')
        chamadas_count = await db.attendances.count_documents({})
        
        print(f"🚨 RESET TOTAL INICIADO por {current_user.email}")
        print(f"   Alunos a serem removidos: {alunos_count}")
        print(f"   Turmas a serem removidas: {turmas_count}")
        print(f"   Chamadas a serem removidas: {chamadas_count}")
        
        # APAGAR TUDO
        result_alunos = await db.alunos.delete_many({})
        result_turmas = await db.turmas.delete_many({})
        # 🎯 CORREÇÃO CRÍTICA: Usar collection 'attendances' (não 'chamadas')
        result_chamadas = await db.attendances.delete_many({})
        
        print(f"✅ RESET CONCLUÍDO:")
        print(f"   Alunos removidos: {result_alunos.deleted_count}")
        print(f"   Turmas removidas: {result_turmas.deleted_count}")
        print(f"   Chamadas removidas: {result_chamadas.deleted_count}")
        
        return {
            "message": "🚨 BANCO RESETADO COMPLETAMENTE",
            "removidos": {
                "alunos": result_alunos.deleted_count,
                "turmas": result_turmas.deleted_count,
                "chamadas": result_chamadas.deleted_count
            },
            "status": "BANCO LIMPO - PRONTO PARA RECOMEÇAR"
        }
        
    except Exception as e:
        print(f"❌ Erro no reset: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro no reset do banco: {str(e)}"
        )

@api_router.get("/debug/students/{user_id}")
async def debug_students_for_user(user_id: str, current_user: UserResponse = Depends(get_current_user)):
    """🔍 DEBUG: Verificar exatamente quais alunos um usuário deveria ver"""
    
    if current_user.tipo != "admin":
        raise HTTPException(status_code=403, detail="Apenas admin pode usar debug")
    
    # Buscar o usuário
    user = await db.usuarios.find_one({"id": user_id})
    if not user:
        return {"error": "Usuário não encontrado"}
    
    # Buscar TODOS os alunos
    todos_alunos = await db.alunos.find({}).to_list(1000)
    
    # Filtrar por created_by
    alunos_created_by = [a for a in todos_alunos if a.get("created_by") == user_id]
    
    # Filtrar por ativo=True
    alunos_ativos = [a for a in todos_alunos if a.get("ativo") == True]
    
    # Filtrar por created_by E ativo
    alunos_filtrados = [a for a in todos_alunos if a.get("created_by") == user_id and a.get("ativo") == True]
    
    # 🔍 ANÁLISE DETALHADA: Encontrar alunos com created_by diferente
    alunos_outros_created_by = [a for a in todos_alunos if a.get("created_by") and a.get("created_by") != user_id]
    alunos_sem_created_by = [a for a in todos_alunos if not a.get("created_by")]
    
    return {
        "usuario": {
            "id": user["id"],
            "nome": user["nome"],
            "tipo": user["tipo"],
            "curso_id": user.get("curso_id"),
            "unidade_id": user.get("unidade_id")
        },
        "totais": {
            "todos_alunos": len(todos_alunos),
            "alunos_created_by": len(alunos_created_by),
            "alunos_ativos": len(alunos_ativos),
            "alunos_filtrados": len(alunos_filtrados),
            "alunos_sem_created_by": len(alunos_sem_created_by),
            "alunos_outros_created_by": len(alunos_outros_created_by)
        },
        "alunos_created_by": [
            {
                "id": a["id"],
                "nome": a["nome"],
                "cpf": a.get("cpf"),
                "ativo": a.get("ativo"),
                "created_by": a.get("created_by"),
                "created_by_name": a.get("created_by_name")
            } for a in alunos_created_by
        ],
        "alunos_filtrados": [
            {
                "id": a["id"],
                "nome": a["nome"],
                "cpf": a.get("cpf"),
                "ativo": a.get("ativo"),
                "created_by": a.get("created_by"),
                "created_by_name": a.get("created_by_name")
            } for a in alunos_filtrados
        ],
        "alunos_sem_created_by": [
            {
                "id": a["id"],
                "nome": a["nome"],
                "cpf": a.get("cpf"),
                "ativo": a.get("ativo"),
                "created_by": a.get("created_by"),
                "created_by_name": a.get("created_by_name")
            } for a in alunos_sem_created_by[:10]  # Máximo 10
        ],
        "alunos_outros_created_by": [
            {
                "id": a["id"],
                "nome": a["nome"],
                "cpf": a.get("cpf"),
                "ativo": a.get("ativo"),
                "created_by": a.get("created_by"),
                "created_by_name": a.get("created_by_name")
            } for a in alunos_outros_created_by[:10]  # Máximo 10
        ]
    }

@api_router.post("/students/bulk-upload")
async def bulk_upload_students(
    file: UploadFile = File(...),
    turma_id: Optional[str] = Query(None, description="ID da turma para associar alunos"),
    curso_id: Optional[str] = Query(None, description="ID do curso (opcional para instrutor)"),
    update_existing: bool = Query(False, description="Se true, atualiza aluno existente por CPF"),
    current_user: UserResponse = Depends(get_current_user),
):
    """
    🚀 UPLOAD EM MASSA DE ALUNOS - SISTEMA AVANÇADO
    
    📋 Formatos aceitos: CSV (.csv) e Excel (.xls/.xlsx)
    📊 Campos obrigatórios: nome_completo, cpf, data_nascimento
    📊 Campos opcionais: email, telefone, rg, genero, endereco
    
    ✅ Validações implementadas:
    - CPF brasileiro com algoritmo de validação
    - Datas em múltiplos formatos (DD/MM/YYYY, YYYY-MM-DD, etc.)
    - Duplicados por CPF (atualizar ou pular)
    - Permissões por tipo de usuário
    
    👨‍🏫 Instrutor: apenas seu curso específico
    📊 Pedagogo: qualquer curso da sua unidade  
    👩‍💻 Monitor: NÃO pode fazer upload
    👑 Admin: sem restrições
    
    🎯 Associação automática à turma se turma_id fornecido
    📊 Retorna resumo detalhado: inseridos/atualizados/pulados/erros
    """
    
    # 🔒 VERIFICAÇÃO DE PERMISSÕES
    if current_user.tipo == "monitor":
        raise HTTPException(
            status_code=403,
            detail="Monitores não podem fazer upload de alunos. Apenas visualizar."
        )
    
    # 🎯 Para instrutor sem curso_id explícito, usar o curso do usuário
    if current_user.tipo == "instrutor" and not curso_id:
        curso_id = getattr(current_user, "curso_id", None)
        if not curso_id:
            raise HTTPException(
                status_code=400,
                detail="Instrutor deve ter curso associado ou fornecer curso_id"
            )
    
    # 📁 VALIDAÇÃO DO ARQUIVO
    if not file.filename:
        raise HTTPException(status_code=400, detail="Nome do arquivo é obrigatório")
    
    filename = file.filename.lower()
    content = await file.read()
    
    if not content:
        raise HTTPException(status_code=400, detail="Arquivo está vazio")
    
    # 📊 PARSING DO ARQUIVO (CSV ou Excel)
    rows: List[Dict[str, Any]] = []
    
    try:
        if filename.endswith(".csv") or not any(filename.endswith(ext) for ext in (".xls", ".xlsx")):
            # 📄 PARSE CSV
            try:
                # Tentar UTF-8 primeiro
                text = content.decode("utf-8", errors="replace")
            except UnicodeDecodeError:
                try:
                    # Fallback Windows-1252 (Excel brasileiro)
                    text = content.decode("windows-1252", errors="replace")
                except UnicodeDecodeError:
                    # Último recurso
                    text = content.decode("iso-8859-1", errors="replace")
            
            # Detectar separador automaticamente
            delimiter = ',' if ',' in text.split('\n')[0] else ';'
            
            reader = csv.DictReader(StringIO(text), delimiter=delimiter)
            for i, r in enumerate(reader, start=2):
                # Limpar dados e adicionar número da linha
                clean_row = {"_line": i}
                for k, v in r.items():
                    if k and v:
                        # Remover BOM e caracteres especiais
                        key_clean = str(k).strip().lstrip('\ufeff').lstrip('�')
                        value_clean = str(v).strip().lstrip('\ufeff').lstrip('�')
                        clean_row[key_clean] = value_clean
                rows.append(clean_row)
                
        else:
            # 📊 PARSE EXCEL (necessita pandas)
            try:
                import pandas as pd
            except ImportError:
                raise HTTPException(
                    status_code=400, 
                    detail="Para upload de Excel é necessário instalar pandas e openpyxl no backend"
                )
            
            try:
                df = pd.read_excel(BytesIO(content), dtype=str)
                df = df.fillna("")  # Substituir NaN por string vazia
                
                for idx, r in df.iterrows():
                    clean_row = {"_line": idx + 2}  # +2 porque header é linha 1
                    for k, v in r.items():
                        if not pd.isna(v) and str(v).strip():
                            clean_row[str(k).strip()] = str(v).strip()
                    rows.append(clean_row)
                    
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Erro ao processar Excel: {str(e)}"
                )
                
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Erro ao ler arquivo: {str(e)}"
        )
    
    if not rows:
        raise HTTPException(
            status_code=400,
            detail="Arquivo sem dados válidos ou cabeçalho incorreto"
        )
    
    # 🔍 FUNÇÃO PARA BUSCAR CAMPOS COM ALIASES
    def get_field(r: Dict[str, Any], *aliases):
        """Busca campo por vários aliases possíveis"""
        for alias in aliases:
            if alias in r and r[alias]:
                return r[alias]
            # Busca case-insensitive com normalização
            alias_norm = alias.lower().replace(" ", "_").replace("-", "_")
            for k in r.keys():
                k_norm = k.lower().replace(" ", "_").replace("-", "_")
                if k_norm == alias_norm and r[k]:
                    return r[k]
        return None
    
    # 📊 CONTADORES E RESULTADOS
    inserted = 0
    updated = 0
    skipped = 0
    errors: List[Dict[str, Any]] = []
    
    print(f"🚀 Iniciando bulk upload: {len(rows)} linhas para processar")
    print(f"👤 Usuário: {current_user.nome} ({current_user.tipo})")
    if curso_id:
        print(f"📚 Curso ID: {curso_id}")
    if turma_id:
        print(f"🎯 Turma ID: {turma_id}")
    
    # 🔄 PROCESSAR CADA LINHA
    for r in rows:
        line = r.get("_line", "?")
        
        try:
            # 📋 EXTRAIR CAMPOS COM ALIASES
            nome = get_field(r, "nome_completo", "nome", "full_name", "student_name")
            data_nasc_raw = get_field(r, "data_nascimento", "data nascimento", "birthdate", "dob", "data_nasc")
            cpf_raw = get_field(r, "cpf", "CPF", "Cpf", "document")
            
            # Campos opcionais
            email = get_field(r, "email", "e-mail", "Email")
            telefone = get_field(r, "telefone", "phone", "celular", "tel")
            rg = get_field(r, "rg", "RG", "identidade")
            genero = get_field(r, "genero", "sexo", "gender")
            endereco = get_field(r, "endereco", "endereço", "address")
            
            # ✅ VALIDAÇÕES BÁSICAS
            if not nome or not cpf_raw:
                errors.append({
                    "line": line,
                    "error": "Nome completo e CPF são obrigatórios",
                    "data": {"nome": nome, "cpf": cpf_raw}
                })
                continue
            
            # ✅ VALIDAÇÃO E NORMALIZAÇÃO CPF
            cpf_norm = normalize_cpf(cpf_raw)
            if not validate_cpf(cpf_norm):
                errors.append({
                    "line": line,
                    "error": f"CPF inválido: {cpf_raw}",
                    "data": {"cpf_original": cpf_raw, "cpf_normalized": cpf_norm}
                })
                continue
            
            # ✅ VALIDAÇÃO DATA DE NASCIMENTO
            data_nasc = None
            if data_nasc_raw:
                try:
                    data_nasc = parse_date_str(data_nasc_raw)
                except Exception as e:
                    errors.append({
                        "line": line,
                        "error": f"Data de nascimento inválida: {data_nasc_raw}",
                        "data": {"data_original": data_nasc_raw, "erro": str(e)}
                    })
                    continue
            
            # 🔍 VERIFICAR SE ALUNO JÁ EXISTE (por CPF)
            existing = await db.alunos.find_one({"cpf": cpf_norm})
            
            if existing:
                if update_existing:
                    # 🔄 ATUALIZAR ALUNO EXISTENTE
                    update_doc = {
                        "nome": nome.strip(),
                        "cpf": cpf_norm,
                        "updated_by": current_user.id,
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }
                    
                    # Adicionar campos opcionais se fornecidos
                    if data_nasc:
                        update_doc["data_nascimento"] = data_nasc.isoformat()
                    if email:
                        update_doc["email"] = email
                    if telefone:
                        update_doc["telefone"] = telefone
                    if rg:
                        update_doc["rg"] = rg
                    if genero:
                        update_doc["genero"] = genero
                    if endereco:
                        update_doc["endereco"] = endereco
                    if curso_id:
                        update_doc["curso_id"] = curso_id
                    
                    await db.alunos.update_one(
                        {"id": existing["id"]}, 
                        {"$set": update_doc}
                    )
                    updated += 1
                    aluno_id_to_use = existing["id"]
                    
                else:
                    # 📊 PULAR ALUNO EXISTENTE
                    skipped += 1
                    aluno_id_to_use = existing["id"]
                    
            else:
                # ➕ CRIAR NOVO ALUNO
                new_id = str(uuid.uuid4())
                doc = {
                    "id": new_id,
                    "nome": nome.strip(),
                    "cpf": cpf_norm,
                    "status": "ativo",
                    "ativo": True,
                    "created_by": current_user.id,
                    "created_by_name": current_user.nome,
                    "created_by_type": current_user.tipo,
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
                
                # Adicionar campos opcionais
                if data_nasc:
                    doc["data_nascimento"] = data_nasc.isoformat()
                if email:
                    doc["email"] = email
                if telefone:
                    doc["telefone"] = telefone
                if rg:
                    doc["rg"] = rg
                if genero:
                    doc["genero"] = genero
                if endereco:
                    doc["endereco"] = endereco
                if curso_id:
                    doc["curso_id"] = curso_id
                
                # Adicionar unidade do usuário se disponível
                if hasattr(current_user, 'unidade_id') and getattr(current_user, 'unidade_id', None):
                    doc["unidade_id"] = getattr(current_user, 'unidade_id', None)
                
                await db.alunos.insert_one(doc)
                inserted += 1
                aluno_id_to_use = new_id
                
            # 🎯 ASSOCIAR À TURMA SE FORNECIDA
            if turma_id and aluno_id_to_use:
                try:
                    # Verificar se turma existe e usuário tem permissão
                    turma = await db.turmas.find_one({"id": turma_id})
                    if turma:
                        # Verificar permissões baseadas no tipo de usuário
                        can_add_to_turma = False
                        
                        if current_user.tipo == "admin":
                            can_add_to_turma = True
                        elif current_user.tipo == "instrutor":
                            # Instrutor: apenas suas turmas
                            if turma["instrutor_id"] == current_user.id:
                                can_add_to_turma = True
                        elif current_user.tipo == "pedagogo":
                            # Pedagogo: turmas da sua unidade
                            if turma.get("unidade_id") == getattr(current_user, 'unidade_id', None):
                                can_add_to_turma = True
                        
                        if can_add_to_turma:
                            # Adicionar aluno à turma (evita duplicatas)
                            await db.turmas.update_one(
                                {"id": turma_id},
                                {"$addToSet": {"alunos_ids": aluno_id_to_use}}
                            )
                        else:
                            print(f"⚠️ Usuário {current_user.email} sem permissão para adicionar à turma {turma_id}")
                    else:
                        print(f"⚠️ Turma {turma_id} não encontrada")
                        
                except Exception as e:
                    print(f"❌ Erro ao associar aluno {aluno_id_to_use} à turma {turma_id}: {e}")
            
        except Exception as e:
            # 🚨 ERRO INESPERADO
            errors.append({
                "line": line,
                "error": f"Erro inesperado: {str(e)}",
                "data": {"exception_type": type(e).__name__}
            })
            print(f"❌ Erro na linha {line}: {e}")
            continue
    
    # 📊 RESUMO FINAL
    summary = {
        "total_processed": len(rows),
        "inserted": inserted,
        "updated": updated,
        "skipped": skipped,
        "errors_count": len(errors),
        "errors": errors[:50],  # Limitar para não sobrecarregar resposta
        "success_rate": f"{((inserted + updated + skipped) / len(rows) * 100):.1f}%" if rows else "0%"
    }
    
    print(f"✅ Bulk upload concluído:")
    print(f"   📊 Total processado: {len(rows)}")
    print(f"   ➕ Inseridos: {inserted}")
    print(f"   🔄 Atualizados: {updated}")
    print(f"   ⏭️ Pulados: {skipped}")
    print(f"   ❌ Erros: {len(errors)}")
    print(f"   📈 Taxa de sucesso: {summary['success_rate']}")
    
    return {
        "success": True,
        "message": f"Upload concluído: {inserted} inseridos, {updated} atualizados, {skipped} pulados, {len(errors)} erros",
        "summary": summary
    }

@api_router.post("/students/import-csv")
async def import_students_csv(
    file: UploadFile = File(...), 
    current_user: UserResponse = Depends(get_current_user)
):
    """📑 IMPORTAÇÃO CSV - LÓGICA REFINADA 29/09/2025
    
    CSV deve conter: nome,cpf,data_nascimento,curso,turma,email,telefone
    
    👨‍🏫 Instrutor: Só aceita curso/unidade dele
    📊 Pedagogo: Só aceita cursos da unidade dele  
    👩‍💻 Monitor: NÃO pode importar
    👑 Admin: Aceita qualquer curso/unidade
    """
    
    # 🔒 MONITOR: Não pode importar alunos
    if current_user.tipo == "monitor":
        raise HTTPException(
            status_code=403, 
            detail="Monitores não podem importar alunos CSV"
        )
    
    # Verificar se arquivo é CSV
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Arquivo deve ser CSV")
    
    # Ler conteúdo do arquivo
    contents = await file.read()
    
    # 🔧 CORREÇÃO: Detectar encoding e separador automaticamente
    try:
        # Tentar UTF-8 primeiro
        csv_content = contents.decode('utf-8')
    except UnicodeDecodeError:
        try:
            # Fallback para Windows-1252 (comum em arquivos Excel brasileiros)
            csv_content = contents.decode('windows-1252')
        except UnicodeDecodeError:
            # Último recurso: ISO-8859-1
            csv_content = contents.decode('iso-8859-1')
    
    # 🔧 CORREÇÃO: Detectar separador (vírgula ou ponto e vírgula)
    delimiter = ',' if ',' in csv_content.split('\n')[0] else ';'
    print(f"🔍 CSV Delimiter detectado: '{delimiter}'")
    
    csv_reader = csv.DictReader(StringIO(csv_content), delimiter=delimiter)
    
    # Validar campos obrigatórios no CSV
    required_fields = ['nome', 'cpf', 'data_nascimento', 'curso']
    if not all(field in csv_reader.fieldnames for field in required_fields):
        raise HTTPException(
            status_code=400, 
            detail=f"CSV deve conter campos: {', '.join(required_fields)}"
        )
    
    # Processar linhas do CSV
    results = {
        'success': [],
        'errors': [],
        'duplicates': [],
        'unauthorized': [],
        'warnings': []  # Para alunos sem turma definida
    }
    
    # Buscar cursos e turmas para validação
    cursos = await db.cursos.find({}).to_list(1000)
    cursos_dict = {curso['nome']: curso for curso in cursos}
    
    # Buscar turmas do usuário para validação de permissões
    turmas = await db.turmas.find({}).to_list(1000)
    turmas_dict = {}
    for turma in turmas:
        key = f"{turma.get('curso_id', '')}_{turma['nome']}"
        turmas_dict[key] = turma
    
    for row_num, row in enumerate(csv_reader, start=2):  # Linha 2+ (header = linha 1)
        try:
            # 🔧 LIMPEZA: Remover caracteres especiais (BOM, �, etc)
            nome_limpo = row['nome'].strip().lstrip('\ufeff').lstrip('�').strip()
            cpf_limpo = row['cpf'].strip().lstrip('\ufeff').lstrip('�').strip()
            data_nascimento_limpa = row['data_nascimento'].strip().lstrip('\ufeff').lstrip('�').strip()
            curso_limpo = row['curso'].strip().lstrip('\ufeff').lstrip('�').strip()
            
            print(f"🔍 Processando linha {row_num}:")
            print(f"   Nome: '{nome_limpo}'")
            print(f"   CPF: '{cpf_limpo}'")
            print(f"   Data: '{data_nascimento_limpa}'")
            print(f"   Curso: '{curso_limpo}'")
            
            # Validar campos obrigatórios
            if not nome_limpo or not cpf_limpo or not data_nascimento_limpa:
                results['errors'].append(f"Linha {row_num}: Campos obrigatórios em branco")
                continue
            
            # 🔧 CORREÇÃO: Converter data de dd/mm/yyyy para yyyy-mm-dd
            try:
                if '/' in data_nascimento_limpa:
                    # Formato brasileiro: dd/mm/yyyy
                    day, month, year = data_nascimento_limpa.split('/')
                    data_nascimento_iso = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                else:
                    # Já está em formato ISO
                    data_nascimento_iso = data_nascimento_limpa
            except ValueError:
                results['errors'].append(f"Linha {row_num}: Data de nascimento inválida: {data_nascimento_limpa}")
                continue
            
            # Validar se curso existe
            if curso_limpo not in cursos_dict:
                # 💡 MELHORIA: Sugerir cursos disponíveis
                cursos_disponiveis = list(cursos_dict.keys())[:5]  # Máximo 5 sugestões
                sugestoes = ", ".join(f"'{c}'" for c in cursos_disponiveis)
                results['errors'].append(
                    f"Linha {row_num}: Curso '{curso_limpo}' não encontrado. " +
                    f"Cursos disponíveis: {sugestoes}{'...' if len(cursos_dict) > 5 else ''}"
                )
                continue
            
            curso = cursos_dict[curso_limpo]
            
            # 🔒 VALIDAÇÃO POR TIPO DE USUÁRIO
            if current_user.tipo == "instrutor":
                # Instrutor: só aceita seu curso
                if curso['id'] != getattr(current_user, 'curso_id', None):
                    results['unauthorized'].append(
                        f"Linha {row_num}: Instrutor não pode importar alunos para curso '{curso['nome']}'"
                    )
                    continue
                    
            elif current_user.tipo == "pedagogo":
                # Pedagogo: só aceita cursos da sua unidade
                if curso.get('unidade_id') != getattr(current_user, 'unidade_id', None):
                    results['unauthorized'].append(
                        f"Linha {row_num}: Pedagogo não pode importar alunos para curso fora da sua unidade"
                    )
                    continue
            
            # Admin: aceita qualquer curso (sem restrições)
            
            # Verificar duplicado (CPF já existe)
            existing_aluno = await db.alunos.find_one({"cpf": cpf_limpo})
            if existing_aluno:
                results['duplicates'].append(f"Linha {row_num}: CPF {cpf_limpo} já cadastrado")
                continue
            
            # 🎯 LÓGICA DE TURMA
            turma_nome = row.get('turma', '').strip()
            turma_id = None
            status_turma = "nao_alocado"  # Default para alunos sem turma
            
            if turma_nome:
                # Buscar turma específica do curso
                turma_key = f"{curso['id']}_{turma_nome}"
                if turma_key in turmas_dict:
                    turma_id = turmas_dict[turma_key]['id']
                    status_turma = "alocado"
                else:
                    # Turma não existe - criar automaticamente se usuário tem permissão
                    if current_user.tipo in ["admin", "instrutor"]:
                        # Criar turma automaticamente
                        nova_turma = {
                            'id': str(uuid.uuid4()),
                            'nome': turma_nome,
                            'curso_id': curso['id'],
                            'unidade_id': curso.get('unidade_id', getattr(current_user, 'unidade_id', None)),
                            'instrutor_id': current_user.id if current_user.tipo == "instrutor" else None,
                            'alunos_ids': [],
                            'ativa': True,
                            'created_at': datetime.now(timezone.utc).isoformat()
                        }
                        await db.turmas.insert_one(nova_turma)
                        turma_id = nova_turma['id']
                        status_turma = "alocado"
                        results['warnings'].append(f"Linha {row_num}: Turma '{turma_nome}' criada automaticamente")
                    else:
                        results['warnings'].append(f"Linha {row_num}: Turma '{turma_nome}' não existe - aluno será marcado como 'não alocado'")
            else:
                results['warnings'].append(f"Linha {row_num}: Sem turma definida - aluno será marcado como 'não alocado'")
            
            # Criar aluno com dados limpos
            aluno_data = {
                'id': str(uuid.uuid4()),
                'nome': nome_limpo,
                'cpf': cpf_limpo,
                'data_nascimento': data_nascimento_iso,
                'email': row.get('email', '').strip().lstrip('\ufeff').lstrip('�').strip(),
                'telefone': row.get('telefone', '').strip().lstrip('\ufeff').lstrip('�').strip(),
                'curso_id': curso['id'],
                'turma_id': turma_id,
                'status_turma': status_turma,
                'status': 'ativo',
                'ativo': True,  # ✅ CRÍTICO: Campo ativo para filtro
                'created_by': current_user.id,  # ID do usuário que importou
                'created_by_name': current_user.nome,  # Nome do usuário que importou
                'created_by_type': current_user.tipo,  # Tipo do usuário que importou
                'created_at': datetime.now(timezone.utc).isoformat()
            }
            
            print(f"🔍 CSV Import - Criando aluno: {nome_limpo}")
            print(f"   created_by: {aluno_data['created_by']}")
            print(f"   created_by_name: {aluno_data['created_by_name']}")
            
            # Inserir aluno no banco
            await db.alunos.insert_one(aluno_data)
            
            # Se turma existe, adicionar aluno à lista de alunos da turma
            if turma_id:
                await db.turmas.update_one(
                    {"id": turma_id},
                    {"$addToSet": {"alunos_ids": aluno_data['id']}}
                )
            
            results['success'].append(f"Linha {row_num}: {nome_limpo} cadastrado com sucesso")
            
        except Exception as e:
            results['errors'].append(f"Linha {row_num}: Erro interno - {str(e)}")
    
    return {
        "message": f"Importação concluída: {len(results['success'])} sucessos, {len(results['errors']) + len(results['duplicates']) + len(results['unauthorized'])} falhas",
        "details": results,
        "summary": {
            "total_processed": len(results['success']) + len(results['errors']) + len(results['duplicates']) + len(results['unauthorized']),
            "successful": len(results['success']),
            "errors": len(results['errors']),
            "duplicates": len(results['duplicates']),
            "unauthorized": len(results['unauthorized']),
            "warnings": len(results['warnings'])
        }
    }

# TURMAS ROUTES
@api_router.post("/classes", response_model=Turma)
async def create_turma(turma_create: TurmaCreate, current_user: UserResponse = Depends(get_current_user)):
    # Admin pode criar qualquer turma
    if current_user.tipo == "admin":
        # Validar se responsável existe e está ativo
        if turma_create.instrutor_id:
            responsavel = await db.usuarios.find_one({
                "id": turma_create.instrutor_id, 
                "tipo": {"$in": ["instrutor", "pedagogo"]}, 
                "status": "ativo"
            })
            if not responsavel:
                raise HTTPException(status_code=400, detail="Responsável não encontrado ou inativo")
            
            # 🎯 DETERMINAR TIPO DE TURMA BASEADO NO RESPONSÁVEL
            if responsavel["tipo"] == "pedagogo":
                turma_create.tipo_turma = "extensao"
            else:
                turma_create.tipo_turma = "regular"
    
    # Instrutor só pode criar turmas do seu próprio curso e unidade
    elif current_user.tipo == "instrutor":
        if not getattr(current_user, 'curso_id', None) or not getattr(current_user, 'unidade_id', None):
            raise HTTPException(status_code=400, detail="Instrutor deve estar associado a um curso e unidade")
        
        # Validar se a turma é do curso e unidade do instrutor
        if turma_create.curso_id != getattr(current_user, 'curso_id', None):
            raise HTTPException(status_code=403, detail="Instrutor só pode criar turmas do seu curso")
        
        if turma_create.unidade_id != getattr(current_user, 'unidade_id', None):
            raise HTTPException(status_code=403, detail="Instrutor só pode criar turmas da sua unidade")
        
        # Definir instrutor automaticamente
        turma_create.instrutor_id = current_user.id
        turma_create.tipo_turma = "regular"  # Turma regular do instrutor
    
    # Pedagogo pode criar turmas de extensão
    elif current_user.tipo == "pedagogo":
        if not getattr(current_user, 'curso_id', None) or not getattr(current_user, 'unidade_id', None):
            raise HTTPException(status_code=400, detail="Pedagogo deve estar associado a um curso e unidade")
        
        # Validar se a turma é do curso e unidade do pedagogo
        if turma_create.curso_id != getattr(current_user, 'curso_id', None):
            raise HTTPException(status_code=403, detail="Pedagogo só pode criar turmas do seu curso")
        
        if turma_create.unidade_id != getattr(current_user, 'unidade_id', None):
            raise HTTPException(status_code=403, detail="Pedagogo só pode criar turmas da sua unidade")
        
        # Definir pedagogo automaticamente
        turma_create.instrutor_id = current_user.id
        turma_create.tipo_turma = "extensao"  # Turma de extensão do pedagogo
    
    else:
        raise HTTPException(status_code=403, detail="Apenas admins, instrutores e pedagogos podem criar turmas")
    
    # Validar se curso e unidade existem
    curso = await db.cursos.find_one({"id": turma_create.curso_id})
    if not curso:
        raise HTTPException(status_code=400, detail="Curso não encontrado")
    
    unidade = await db.unidades.find_one({"id": turma_create.unidade_id})
    if not unidade:
        raise HTTPException(status_code=400, detail="Unidade não encontrada")
    
    turma_dict = prepare_for_mongo(turma_create.dict())
    turma_obj = Turma(**turma_dict)
    
    mongo_data = prepare_for_mongo(turma_obj.dict())
    await db.turmas.insert_one(mongo_data)
    return turma_obj

@api_router.get("/classes", response_model=List[Turma])
async def get_turmas(current_user: UserResponse = Depends(get_current_user)):
    if current_user.tipo == "admin":
        turmas_raw = await db.turmas.find({"ativo": True}).to_list(1000)
        # Processar turmas admin e garantir compatibilidade
        result_turmas = []
        for turma in turmas_raw:
            try:
                parsed_turma = parse_from_mongo(turma)
                if 'ciclo' not in parsed_turma or parsed_turma['ciclo'] is None:
                    parsed_turma['ciclo'] = None
                turma_obj = Turma(**parsed_turma)
                result_turmas.append(turma_obj)
            except Exception as e:
                print(f"⚠️ Admin - Erro ao processar turma {turma.get('id', 'SEM_ID')}: {e}")
                parsed_turma = parse_from_mongo(turma)
                parsed_turma['ciclo'] = None
                try:
                    turma_obj = Turma(**parsed_turma)
                    result_turmas.append(turma_obj)
                except Exception as e2:
                    print(f"❌ Admin - Erro crítico turma {turma.get('id', 'SEM_ID')}: {e2}")
                    continue
        return result_turmas
    else:
        # Instrutor, pedagogo ou monitor vê turmas do seu curso e unidade
        query = {"ativo": True}
        
        if current_user.tipo == "instrutor":
            # Instrutor vê suas próprias turmas do curso
            query["instrutor_id"] = current_user.id
            if getattr(current_user, 'curso_id', None):
                query["curso_id"] = getattr(current_user, 'curso_id', None)
            if getattr(current_user, 'unidade_id', None):
                query["unidade_id"] = getattr(current_user, 'unidade_id', None)
        
        elif current_user.tipo in ["pedagogo", "monitor"]:
            # Pedagogo e monitor veem turmas do seu curso e unidade
            if getattr(current_user, 'curso_id', None):
                query["curso_id"] = getattr(current_user, 'curso_id', None)
            if getattr(current_user, 'unidade_id', None):
                query["unidade_id"] = getattr(current_user, 'unidade_id', None)
            # 🎯 CORREÇÃO: Pedagogo só vê turmas de EXTENSÃO
            if current_user.tipo == "pedagogo":
                query["tipo_turma"] = "extensao"
        
        turmas = await db.turmas.find(query).to_list(1000)
    
    # Processar turmas e garantir compatibilidade com dados antigos
    result_turmas = []
    for turma in turmas:
        try:
            parsed_turma = parse_from_mongo(turma)
            # Garantir que campo ciclo existe (compatibilidade com dados antigos)
            if 'ciclo' not in parsed_turma or parsed_turma['ciclo'] is None:
                parsed_turma['ciclo'] = None
            turma_obj = Turma(**parsed_turma)
            result_turmas.append(turma_obj)
        except Exception as e:
            print(f"⚠️ Erro ao processar turma {turma.get('id', 'SEM_ID')}: {e}")
            # Adicionar campos faltantes para compatibilidade
            parsed_turma = parse_from_mongo(turma)
            parsed_turma['ciclo'] = None  # Campo obrigatório faltante
            try:
                turma_obj = Turma(**parsed_turma)
                result_turmas.append(turma_obj)
            except Exception as e2:
                print(f"❌ Erro crítico ao processar turma {turma.get('id', 'SEM_ID')}: {e2}")
                continue
    
    return result_turmas

@api_router.put("/classes/{turma_id}/students/{aluno_id}")
async def add_aluno_to_turma(turma_id: str, aluno_id: str, current_user: UserResponse = Depends(get_current_user)):
    # Check if turma exists
    turma = await db.turmas.find_one({"id": turma_id})
    if not turma:
        raise HTTPException(status_code=404, detail="Turma não encontrada")
    
    # Verificar permissões baseadas no curso/unidade
    if current_user.tipo == "admin":
        # Admin pode adicionar qualquer aluno
        pass
    elif current_user.tipo == "instrutor":
        # Instrutor só pode adicionar alunos em suas próprias turmas
        if turma["instrutor_id"] != current_user.id:
            raise HTTPException(status_code=403, detail="Instrutor só pode gerenciar suas próprias turmas")
    elif current_user.tipo in ["pedagogo", "monitor"]:
        # Pedagogo/monitor só pode adicionar em turmas do seu curso e unidade
        if (getattr(current_user, 'curso_id', None) and turma["curso_id"] != getattr(current_user, 'curso_id', None)) or \
           (getattr(current_user, 'unidade_id', None) and turma["unidade_id"] != getattr(current_user, 'unidade_id', None)):
            raise HTTPException(status_code=403, detail="Acesso negado: turma fora do seu curso/unidade")
    else:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    if len(turma.get("alunos_ids", [])) >= turma.get("vagas_total", 30):
        raise HTTPException(status_code=400, detail="Turma está lotada")
    
    # Verificar se aluno existe
    aluno = await db.alunos.find_one({"id": aluno_id})
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    
    # Add aluno to turma
    await db.turmas.update_one(
        {"id": turma_id},
        {
            "$addToSet": {"alunos_ids": aluno_id},
            "$inc": {"vagas_ocupadas": 1}
        }
    )
    
    return {"message": "Aluno adicionado à turma"}

@api_router.delete("/classes/{turma_id}/students/{aluno_id}")
async def remove_aluno_from_turma(turma_id: str, aluno_id: str, current_user: UserResponse = Depends(get_current_user)):
    check_admin_permission(current_user)
    
    await db.turmas.update_one(
        {"id": turma_id},
        {
            "$pull": {"alunos_ids": aluno_id},
            "$inc": {"vagas_ocupadas": -1}
        }
    )
    
    return {"message": "Aluno removido da turma"}

@api_router.delete("/classes/{turma_id}")
async def delete_turma(turma_id: str, current_user: UserResponse = Depends(get_current_user)):
    """🗑️ DELETAR TURMA - Apenas Admin pode deletar turmas"""
    
    # 🔒 VERIFICAÇÃO: Apenas admin pode deletar turmas
    if current_user.tipo != "admin":
        raise HTTPException(
            status_code=403, 
            detail="Apenas administradores podem deletar turmas"
        )
    
    # Verificar se turma existe
    turma = await db.turmas.find_one({"id": turma_id})
    if not turma:
        raise HTTPException(status_code=404, detail="Turma não encontrada")
    
    # 🗑️ ADMIN PODE DELETAR FORÇADAMENTE
    # Remover alunos da turma primeiro (se houver)
    if turma.get('alunos_ids') and len(turma.get('alunos_ids', [])) > 0:
        print(f"🔄 Removendo {len(turma['alunos_ids'])} aluno(s) da turma antes de deletar")
        # Limpar referências da turma nos alunos se necessário (futuro)
    
    # Deletar chamadas relacionadas (se houver)
    # 🎯 CORREÇÃO CRÍTICA: Usar collection 'attendances' (não 'chamadas')
    chamadas_count = await db.attendances.count_documents({"turma_id": turma_id})
    if chamadas_count > 0:
        print(f"🗑️ Deletando {chamadas_count} chamada(s) relacionada(s)")
        await db.attendances.delete_many({"turma_id": turma_id})
    
    # 🗑️ DELETAR TURMA
    result = await db.turmas.delete_one({"id": turma_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=500, detail="Erro ao deletar turma")
    
    print(f"🗑️ Admin {current_user.nome} deletou turma: {turma.get('nome', 'SEM_NOME')} (ID: {turma_id})")
    
    return {
        "message": f"Turma '{turma.get('nome', 'SEM_NOME')}' deletada com sucesso",
        "turma_deletada": {
            "id": turma_id,
            "nome": turma.get('nome'),
            "curso_nome": turma.get('curso_nome', 'N/A'),
            "instrutor_nome": turma.get('instrutor_nome', 'N/A')
        }
    }

@api_router.put("/classes/{turma_id}", response_model=Turma)
async def update_turma(turma_id: str, turma_update: TurmaUpdate, current_user: UserResponse = Depends(get_current_user)):
    """✏️ ATUALIZAR TURMA - Admin, Instrutor (suas turmas) ou Pedagogo (suas turmas)"""
    
    # Verificar se turma existe
    turma_existente = await db.turmas.find_one({"id": turma_id})
    if not turma_existente:
        raise HTTPException(status_code=404, detail="Turma não encontrada")
    
    # 🔒 VERIFICAÇÃO DE PERMISSÕES
    if current_user.tipo == "instrutor":
        # Instrutor só pode atualizar suas próprias turmas
        if turma_existente["instrutor_id"] != current_user.id:
            raise HTTPException(
                status_code=403, 
                detail="Você só pode atualizar suas próprias turmas"
            )
    elif current_user.tipo == "pedagogo":
        # Pedagogo só pode atualizar turmas do seu curso/unidade
        if (getattr(current_user, 'curso_id', None) and turma_existente["curso_id"] != getattr(current_user, 'curso_id', None)) or \
           (getattr(current_user, 'unidade_id', None) and turma_existente["unidade_id"] != getattr(current_user, 'unidade_id', None)):
            raise HTTPException(
                status_code=403, 
                detail="Você só pode atualizar turmas do seu curso/unidade"
            )
    elif current_user.tipo == "monitor":
        # Monitor não pode atualizar turmas
        raise HTTPException(
            status_code=403, 
            detail="Monitores não podem atualizar turmas"
        )
    # Admin pode atualizar qualquer turma (sem restrições)
    
    # 📝 PREPARAR DADOS PARA ATUALIZAÇÃO
    update_data = {}
    
    # Campos que podem ser atualizados diretamente
    for field in ["nome", "data_inicio", "data_fim", "horario_inicio", "horario_fim", "dias_semana", "tipo_turma", "vagas_total", "instrutor_id"]:
        value = getattr(turma_update, field)
        if value is not None:
            if field in ["data_inicio", "data_fim"] and isinstance(value, date):
                update_data[field] = value.isoformat()
            else:
                update_data[field] = value
    
    # Se não há nada para atualizar
    if not update_data:
        raise HTTPException(status_code=400, detail="Nenhum campo válido fornecido para atualização")
    
    # 📅 VALIDAÇÃO DE DATAS
    if "data_inicio" in update_data and "data_fim" in update_data:
        data_inicio = datetime.fromisoformat(update_data["data_inicio"]).date()
        data_fim = datetime.fromisoformat(update_data["data_fim"]).date()
        if data_inicio >= data_fim:
            raise HTTPException(status_code=400, detail="Data de início deve ser anterior à data de fim")
    
    # 🕒 VALIDAÇÃO DE HORÁRIOS
    if "horario_inicio" in update_data and "horario_fim" in update_data:
        try:
            h_inicio = datetime.strptime(update_data["horario_inicio"], "%H:%M").time()
            h_fim = datetime.strptime(update_data["horario_fim"], "%H:%M").time()
            if h_inicio >= h_fim:
                raise HTTPException(status_code=400, detail="Horário de início deve ser anterior ao horário de fim")
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de horário inválido. Use HH:MM")
    
    # ✅ EXECUTAR ATUALIZAÇÃO
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    result = await db.turmas.update_one(
        {"id": turma_id},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        # Verificar se realmente não houve mudanças ou se foi erro
        turma_verificacao = await db.turmas.find_one({"id": turma_id})
        if not turma_verificacao:
            raise HTTPException(status_code=404, detail="Turma não encontrada")
        # Se chegou aqui, provavelmente não houve mudanças (valores iguais)
    
    # 📊 BUSCAR TURMA ATUALIZADA
    turma_atualizada = await db.turmas.find_one({"id": turma_id})
    
    # Buscar informações complementares (curso, unidade, instrutor)
    curso = await db.cursos.find_one({"id": turma_atualizada["curso_id"]})
    unidade = await db.unidades.find_one({"id": turma_atualizada["unidade_id"]})
    instrutor = await db.usuarios.find_one({"id": turma_atualizada["instrutor_id"]})
    
    # Preparar dados para resposta
    turma_atualizada["curso_nome"] = curso["nome"] if curso else "Curso não encontrado"
    turma_atualizada["unidade_nome"] = unidade["nome"] if unidade else "Unidade não encontrada"
    turma_atualizada["instrutor_nome"] = instrutor["nome"] if instrutor else "Instrutor não encontrado"
    
    print(f"✏️ {current_user.tipo.title()} {current_user.nome} atualizou turma: {turma_atualizada['nome']} (ID: {turma_id})")
    print(f"   Campos atualizados: {list(update_data.keys())}")
    
    return parse_from_mongo(turma_atualizada)

# CHAMADA ROUTES
@api_router.post("/attendance", response_model=Chamada)
async def create_chamada(chamada_create: ChamadaCreate, current_user: UserResponse = Depends(get_current_user)):
    # 🔒 VALIDAÇÃO DE DATA: Só pode fazer chamada do dia atual
    data_chamada = chamada_create.data
    data_hoje = date.today()
    
    if data_chamada != data_hoje:
        raise HTTPException(
            status_code=400, 
            detail=f"Só é possível fazer chamada da data atual ({data_hoje.strftime('%d/%m/%Y')})"
        )
    
    # 🔒 VALIDAÇÃO: Verificar se já existe chamada para esta turma hoje
    chamada_existente = await db.attendances.find_one({
        "turma_id": chamada_create.turma_id,
        "data": data_hoje.isoformat()
    })
    
    if chamada_existente:
        raise HTTPException(
            status_code=400,
            detail=f"Chamada já foi realizada para esta turma hoje ({data_hoje.strftime('%d/%m/%Y')})"
        )
    
    # Verificar permissões da turma
    turma = await db.turmas.find_one({"id": chamada_create.turma_id})
    if not turma:
        raise HTTPException(status_code=404, detail="Turma não encontrada")
    
    # Verificar se o usuário pode fazer chamada nesta turma
    if current_user.tipo == "instrutor":
        if turma["instrutor_id"] != current_user.id:
            raise HTTPException(status_code=403, detail="Você só pode fazer chamada das suas turmas")
    elif current_user.tipo in ["pedagogo", "monitor"]:
        if (getattr(current_user, 'curso_id', None) and turma["curso_id"] != getattr(current_user, 'curso_id', None)) or \
           (getattr(current_user, 'unidade_id', None) and turma["unidade_id"] != getattr(current_user, 'unidade_id', None)):
            raise HTTPException(status_code=403, detail="Acesso negado: turma fora do seu curso/unidade")
    elif current_user.tipo != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    # 🕐 Adicionar hora de registro para alunos presentes
    hora_atual = datetime.now().strftime("%H:%M")
    presencas_com_hora = {}
    
    for aluno_id, dados_presenca in chamada_create.presencas.items():
        presencas_com_hora[aluno_id] = {
            "presente": dados_presenca.get("presente", False),
            "justificativa": dados_presenca.get("justificativa", ""),
            "atestado_id": dados_presenca.get("atestado_id", ""),
            # 📝 Registrar hora apenas se estiver presente
            "hora_registro": hora_atual if dados_presenca.get("presente", False) else ""
        }
    
    # Calculate totals
    total_presentes = sum(1 for p in presencas_com_hora.values() if p.get("presente", False))
    total_faltas = len(presencas_com_hora) - total_presentes
    
    chamada_dict = prepare_for_mongo(chamada_create.dict())
    chamada_dict.update({
        "instrutor_id": current_user.id,
        "total_presentes": total_presentes,
        "total_faltas": total_faltas,
        "presencas": presencas_com_hora  # 🕐 Usar presencas com hora
    })
    
    chamada_obj = Chamada(**chamada_dict)
    mongo_data = prepare_for_mongo(chamada_obj.dict())
    # 🎯 CORREÇÃO CRÍTICA: Usar collection 'attendances' (não 'chamadas')
    await db.attendances.insert_one(mongo_data)
    
    return chamada_obj

@api_router.get("/classes/{turma_id}/attendance", response_model=List[Chamada])
async def get_chamadas_turma(turma_id: str, current_user: UserResponse = Depends(get_current_user)):
    # 🎯 CORREÇÃO CRÍTICA: Usar collection 'attendances' (não 'chamadas')
    chamadas = await db.attendances.find({"turma_id": turma_id}).to_list(1000)
    return [Chamada(**parse_from_mongo(chamada)) for chamada in chamadas]

@api_router.get("/classes/{turma_id}/students")
async def get_turma_students(turma_id: str, current_user: UserResponse = Depends(get_current_user)):
    turma = await db.turmas.find_one({"id": turma_id})
    if not turma:
        raise HTTPException(status_code=404, detail="Turma não encontrada")
    
    aluno_ids = turma.get("alunos_ids", [])
    if not aluno_ids:
        return []
    
    # 🚫 FILTRAR ALUNOS: Excluir desistentes da lista de chamada
    alunos = await db.alunos.find({
        "id": {"$in": aluno_ids}, 
        "ativo": True,
        "status": {"$ne": "desistente"}  # Excluir alunos desistentes
    }).to_list(1000)
    
    # Clean up MongoDB-specific fields and parse dates
    result = []
    for aluno in alunos:
        # Remove MongoDB ObjectId field
        if '_id' in aluno:
            del aluno['_id']
        # Parse dates and clean up the data
        cleaned_aluno = parse_from_mongo(aluno)
        result.append(cleaned_aluno)
    
    return result

# 🏥 SISTEMA DE ATESTADOS MÉDICOS COMPLETO
@api_router.post("/upload/atestado")
async def upload_atestado(
    file: UploadFile = File(...), 
    aluno_id: str = Form(...),
    observacao: Optional[str] = Form(None),
    current_user: UserResponse = Depends(get_current_user)
):
    """📋 Upload de atestado médico para justificar falta de aluno"""
    
    # 🔒 VALIDAÇÃO DE PERMISSÕES
    if current_user.tipo not in ["admin", "instrutor", "pedagogo"]:
        raise HTTPException(status_code=403, detail="Apenas admin, instrutor e pedagogo podem anexar atestados")
    
    # ✅ VALIDAÇÃO DE ARQUIVO
    if file.content_type not in ["image/jpeg", "image/png", "application/pdf"]:
        raise HTTPException(status_code=400, detail="Apenas arquivos PDF, JPG e PNG são aceitos")
    
    # Verificar tamanho (máx 5MB)
    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:  # 5MB
        raise HTTPException(status_code=400, detail="Arquivo muito grande. Máximo 5MB")
    
    # 🔍 VERIFICAR SE ALUNO EXISTE E PERMISSÕES
    aluno = await db.alunos.find_one({"id": aluno_id})
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    
    # Para não-admin: verificar permissões do aluno
    if current_user.tipo != "admin":
        tem_permissao = False
        
        if current_user.tipo == "instrutor":
            # Instrutor: só pode anexar atestado de alunos das suas turmas
            turmas_instrutor = await db.turmas.find({
                "instrutor_id": current_user.id,
                "alunos_ids": aluno_id
            }).to_list(10)
            tem_permissao = len(turmas_instrutor) > 0
            
        elif current_user.tipo == "pedagogo":
            # Pedagogo: só pode anexar atestado de alunos da sua unidade
            turmas_unidade = await db.turmas.find({
                "unidade_id": getattr(current_user, 'unidade_id', None),
                "alunos_ids": aluno_id
            }).to_list(10)
            tem_permissao = len(turmas_unidade) > 0
        
        if not tem_permissao:
            raise HTTPException(
                status_code=403, 
                detail="Você só pode anexar atestados de alunos das suas turmas/unidade"
            )
    
    # 💾 SALVAR NO GRIDFS
    try:
        file_id = await fs_bucket.upload_from_stream(
            file.filename,
            BytesIO(contents),
            metadata={
                "content_type": file.content_type,
                "aluno_id": aluno_id,
                "uploaded_by": current_user.id,
                "observacao": observacao,
                "tipo": "atestado_medico"
            }
        )
        
        # 📝 REGISTRAR ATESTADO
        atestado_data = {
            "id": str(uuid.uuid4()),
            "aluno_id": aluno_id,
            "aluno_nome": aluno.get("nome", ""),
            "file_id": str(file_id),
            "filename": file.filename,
            "content_type": file.content_type,
            "observacao": observacao or "",
            "data_envio": date.today(),
            "uploaded_by": current_user.id,
            "uploaded_by_nome": current_user.nome,
            "created_at": datetime.now(timezone.utc)
        }
        
        await db.atestados.insert_one(atestado_data)
        
        return {
            "id": atestado_data["id"],
            "file_id": str(file_id),
            "filename": file.filename,
            "message": "Atestado anexado com sucesso"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar atestado: {str(e)}")

@api_router.get("/alunos/{aluno_id}/atestados")
async def listar_atestados_aluno(
    aluno_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """📋 Listar todos os atestados de um aluno específico"""
    
    # 🔒 VALIDAÇÃO DE PERMISSÕES (mesmo padrão do upload)
    if current_user.tipo not in ["admin", "instrutor", "pedagogo"]:
        raise HTTPException(status_code=403, detail="Permissão negada")
    
    # Verificar se aluno existe
    aluno = await db.alunos.find_one({"id": aluno_id})
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    
    # Para não-admin: verificar permissões
    if current_user.tipo != "admin":
        tem_permissao = False
        
        if current_user.tipo == "instrutor":
            turmas_instrutor = await db.turmas.find({
                "instrutor_id": current_user.id,
                "alunos_ids": aluno_id
            }).to_list(10)
            tem_permissao = len(turmas_instrutor) > 0
            
        elif current_user.tipo == "pedagogo":
            turmas_unidade = await db.turmas.find({
                "unidade_id": getattr(current_user, 'unidade_id', None),
                "alunos_ids": aluno_id
            }).to_list(10)
            tem_permissao = len(turmas_unidade) > 0
        
        if not tem_permissao:
            raise HTTPException(status_code=403, detail="Sem permissão para visualizar atestados deste aluno")
    
    # 📋 BUSCAR ATESTADOS
    atestados = await db.atestados.find({"aluno_id": aluno_id}).sort("created_at", -1).to_list(100)
    
    return {
        "aluno_id": aluno_id,
        "aluno_nome": aluno.get("nome", ""),
        "total_atestados": len(atestados),
        "atestados": atestados
    }

@api_router.get("/atestados/{atestado_id}/download")
async def download_atestado(
    atestado_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """📥 Download de arquivo de atestado"""
    
    # 🔍 BUSCAR ATESTADO
    atestado = await db.atestados.find_one({"id": atestado_id})
    if not atestado:
        raise HTTPException(status_code=404, detail="Atestado não encontrado")
    
    # 🔒 VALIDAÇÃO DE PERMISSÕES (mesmo padrão)
    if current_user.tipo not in ["admin", "instrutor", "pedagogo"]:
        raise HTTPException(status_code=403, detail="Permissão negada")
    
    if current_user.tipo != "admin":
        tem_permissao = False
        aluno_id = atestado["aluno_id"]
        
        if current_user.tipo == "instrutor":
            turmas_instrutor = await db.turmas.find({
                "instrutor_id": current_user.id,
                "alunos_ids": aluno_id
            }).to_list(10)
            tem_permissao = len(turmas_instrutor) > 0
            
        elif current_user.tipo == "pedagogo":
            turmas_unidade = await db.turmas.find({
                "unidade_id": getattr(current_user, 'unidade_id', None),
                "alunos_ids": aluno_id
            }).to_list(10)
            tem_permissao = len(turmas_unidade) > 0
        
        if not tem_permissao:
            raise HTTPException(status_code=403, detail="Sem permissão para baixar este atestado")
    
    # 📥 BUSCAR ARQUIVO NO GRIDFS
    try:
        file_id = ObjectId(atestado["file_id"])
        grid_out = await fs_bucket.open_download_stream(file_id)
        
        contents = await grid_out.read()
        
        return StreamingResponse(
            BytesIO(contents),
            media_type=atestado["content_type"],
            headers={"Content-Disposition": f"attachment; filename={atestado['filename']}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao baixar arquivo: {str(e)}")

@api_router.get("/desistencias/motivos")
async def get_motivos_desistencia():
    """📝 Lista de motivos padrão para desistência - endpoint público"""
    
    MOTIVOS_DESISTENCIA = [
        {
            "codigo": "conflito_horario_escola",
            "descricao": "CONFLITO ENTRE O HORÁRIO DO CURSO E ESCOLA"
        },
        {
            "codigo": "conflito_curso_trabalho",
            "descricao": "CONFLITO ENTRE CURSO E TRABALHO"
        },
        {
            "codigo": "problemas_saude",
            "descricao": "PROBLEMAS DE SAÚDE (ALUNO OU FAMILIAR)"
        },
        {
            "codigo": "sem_retorno_contato",
            "descricao": "SEM RETORNO DE CONTATO"
        },
        {
            "codigo": "conseguiu_trabalho",
            "descricao": "CONSEGUIU UM TRABALHO"
        },
        {
            "codigo": "lactantes_gestantes",
            "descricao": "LACTANTES, GESTANTES OU EM INÍCIO DE GESTAÇÃO"
        },
        {
            "codigo": "nao_identificou_curso",
            "descricao": "NÃO SE IDENTIFICOU COM O CURSO"
        },
        {
            "codigo": "dificuldades_acompanhamento",
            "descricao": "DIFICULDADES DE ACOMPANHAMENTO DO CURSO"
        },
        {
            "codigo": "curso_fora_ios",
            "descricao": "OPTOU POR UM CURSO FORA DO IOS"
        },
        {
            "codigo": "sem_recursos_transporte",
            "descricao": "SEM RECURSOS FINANCEIROS PARA O TRANSPORTE"
        },
        {
            "codigo": "mudou_endereco",
            "descricao": "MUDOU DE ENDEREÇO"
        },
        {
            "codigo": "cuidar_familiar",
            "descricao": "PRECISOU CUIDAR DA/O IRMÃ/ÃO OU DE OUTRO FAMILIAR"
        },
        {
            "codigo": "servico_militar",
            "descricao": "CONVOCAÇÃO DO SERVIÇO MILITAR"
        },
        {
            "codigo": "outro",
            "descricao": "OUTRO (PREENCHIMENTO PERSONALIZADO)"
        }
    ]
    
    return MOTIVOS_DESISTENCIA

# DESISTENTES ROUTES
@api_router.post("/dropouts", response_model=Desistente)
async def create_desistente(desistente_create: DesistenteCreate, current_user: UserResponse = Depends(get_current_user)):
    # 🔒 VALIDAÇÃO DE PERMISSÕES: Verificar se usuário pode registrar desistência deste aluno
    if current_user.tipo not in ["admin", "instrutor", "pedagogo"]:
        raise HTTPException(status_code=403, detail="Apenas admin, instrutor e pedagogo podem registrar desistências")
    
    # Verificar se o aluno existe
    aluno = await db.alunos.find_one({"id": desistente_create.aluno_id})
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    
    # Para não-admin: verificar se o aluno está nas turmas do usuário
    if current_user.tipo != "admin":
        # Buscar turmas que contêm este aluno
        turmas_aluno = await db.turmas.find({
            "alunos_ids": desistente_create.aluno_id,
            "ativo": True
        }).to_list(1000)
        
        # Verificar permissões baseadas no tipo de usuário
        tem_permissao = False
        
        if current_user.tipo == "instrutor":
            # Instrutor: pode registrar desistência de alunos das suas turmas
            for turma in turmas_aluno:
                if turma.get("instrutor_id") == current_user.id:
                    tem_permissao = True
                    break
                    
        elif current_user.tipo == "pedagogo":
            # Pedagogo: pode registrar desistência de alunos da sua unidade
            for turma in turmas_aluno:
                if turma.get("unidade_id") == getattr(current_user, 'unidade_id', None):
                    tem_permissao = True
                    break
        
        if not tem_permissao:
            raise HTTPException(
                status_code=403, 
                detail="Você só pode registrar desistência de alunos das suas turmas/unidade"
            )
    
    # 📝 PREPARAR DADOS DA DESISTÊNCIA
    desistente_dict = prepare_for_mongo(desistente_create.dict())
    desistente_dict["registrado_por"] = current_user.id
    desistente_dict["registrado_por_nome"] = current_user.nome
    desistente_dict["aluno_nome"] = aluno.get("nome", "")
    
    desistente_obj = Desistente(**desistente_dict)
    mongo_data = prepare_for_mongo(desistente_obj.dict())
    await db.desistentes.insert_one(mongo_data)
    
    # Update aluno status
    await db.alunos.update_one(
        {"id": desistente_create.aluno_id},
        {"$set": {"status": "desistente"}}
    )
    
    # 🔄 REMOVER ALUNO DAS TURMAS: Para não aparecer mais nas chamadas
    await db.turmas.update_many(
        {"alunos_ids": desistente_create.aluno_id},
        {"$pull": {"alunos_ids": desistente_create.aluno_id}}
    )
    
    return desistente_obj

@api_router.get("/dropouts", response_model=List[Desistente])
async def get_desistentes(
    skip: int = 0,
    limit: int = 100,
    turma_id: Optional[str] = None,
    current_user: UserResponse = Depends(get_current_user)
):
    query = {}
    if turma_id:
        query["turma_id"] = turma_id
        
    desistentes = await db.desistentes.find(query).skip(skip).limit(limit).to_list(limit)
    return [Desistente(**parse_from_mongo(desistente)) for desistente in desistentes]

# � REATIVAÇÃO DE ALUNOS DESISTENTES (APENAS ADMIN)
@api_router.post("/students/{student_id}/reactivate")
async def reactivate_student(
    student_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    ⚡ Reativar aluno desistente (APENAS ADMIN)
    - Altera status de 'desistente' para 'ativo'
    - Remove registro da tabela de desistentes
    - Permite que aluno seja matriculado em novas turmas
    """
    
    # 🔒 VALIDAÇÃO: Apenas admin pode reativar alunos
    if current_user.tipo != "admin":
        raise HTTPException(
            status_code=403, 
            detail="Apenas administradores podem reativar alunos desistentes"
        )
    
    # 🔍 VERIFICAR SE ALUNO EXISTE
    aluno = await db.alunos.find_one({"id": student_id})
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    
    # ✅ VERIFICAR SE ALUNO ESTÁ REALMENTE COMO DESISTENTE
    if aluno.get("status") != "desistente":
        raise HTTPException(
            status_code=400, 
            detail=f"Aluno está com status '{aluno.get('status')}', não pode ser reativado"
        )
    
    try:
        # 🔄 ATUALIZAR STATUS DO ALUNO PARA ATIVO
        await db.alunos.update_one(
            {"id": student_id},
            {"$set": {"status": "ativo", "data_reativacao": datetime.now(timezone.utc)}}
        )
        
        # 🗑️ REMOVER DA TABELA DE DESISTENTES
        result = await db.desistentes.delete_many({"aluno_id": student_id})
        
        # 📊 LOG DA OPERAÇÃO
        print(f"🔄 REATIVAÇÃO: Aluno {aluno.get('nome')} reativado por admin {current_user.nome}")
        print(f"   📝 Registros de desistência removidos: {result.deleted_count}")
        
        return {
            "message": "Aluno reativado com sucesso",
            "student_id": student_id,
            "student_name": aluno.get("nome"),
            "previous_status": "desistente",
            "new_status": "ativo",
            "reactivated_by": current_user.nome,
            "reactivated_at": datetime.now(timezone.utc).isoformat(),
            "dropout_records_removed": result.deleted_count
        }
        
    except Exception as e:
        print(f"❌ Erro na reativação: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Erro interno ao reativar aluno: {str(e)}"
        )

# �📋 JUSTIFICATIVAS/ATESTADOS ROUTES
@api_router.post("/students/{student_id}/justifications")
async def create_justification(
    student_id: str,
    attendance_id: Optional[str] = Form(None),
    reason_code: str = Form(...),
    reason_text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Criar nova justificativa/atestado para um aluno
    - Pode ser vinculada a uma chamada específica (attendance_id)
    - Arquivo opcional (PDF, PNG, JPG até 5MB)
    - Motivo obrigatório usando códigos padronizados
    """
    
    # 1. Verificar permissões
    can_manage = await user_can_manage_student(current_user, student_id)
    if not can_manage:
        raise HTTPException(
            status_code=403, 
            detail="Você não tem permissão para gerenciar este aluno"
        )
    
    # 2. Validar código do motivo
    if reason_code not in ALLOWED_REASON_CODES:
        raise HTTPException(
            status_code=400, 
            detail=f"Código de motivo inválido. Use um dos: {list(ALLOWED_REASON_CODES.keys())}"
        )
    
    # 3. Validar reason_text quando CUSTOM
    if reason_code == "CUSTOM" and not reason_text:
        raise HTTPException(
            status_code=400,
            detail="Campo 'reason_text' é obrigatório quando reason_code = CUSTOM"
        )
    
    # 4. Validar arquivo se fornecido
    file_meta = {}
    if file:
        # Validar tipo de arquivo
        allowed_types = ["application/pdf", "image/png", "image/jpeg", "image/jpg"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail="Tipo de arquivo não permitido. Use PDF, PNG ou JPG"
            )
        
        # Ler conteúdo e validar tamanho
        contents = await file.read()
        if len(contents) > 5 * 1024 * 1024:  # 5MB
            raise HTTPException(
                status_code=400,
                detail="Arquivo muito grande. Máximo 5MB"
            )
        
        # Salvar no GridFS
        try:
            file_id = await fs_bucket.upload_from_stream(
                file.filename,
                contents,
                metadata={
                    "content_type": file.content_type,
                    "uploaded_by": current_user.id,
                    "student_id": student_id
                }
            )
            file_meta = {
                "file_id": str(file_id),
                "file_name": file.filename,
                "file_mime": file.content_type,
                "file_size": len(contents)
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao salvar arquivo: {str(e)}")
    
    # 5. Criar documento de justificativa
    justification_data = {
        "id": str(uuid.uuid4()),
        "student_id": student_id,
        "attendance_id": attendance_id,
        "uploaded_by": current_user.id,
        "uploaded_by_name": current_user.nome,
        "uploaded_at": datetime.now(timezone.utc),
        "reason_code": reason_code,
        "reason_text": reason_text,
        "status": "registered",
        "visible_to_student": True,
        **file_meta
    }
    
    # 6. Salvar no banco
    await db.justifications.insert_one(justification_data)
    
    # 7. Se vinculado a uma chamada, marcar como justificado
    if attendance_id:
        await db.chamadas.update_one(
            {"id": attendance_id, f"presencas.{student_id}": {"$exists": True}},
            {"$set": {f"presencas.{student_id}.justificado": True, f"presencas.{student_id}.justification_id": justification_data["id"]}}
        )
    
    return {"ok": True, "justification_id": justification_data["id"], "message": "Justificativa criada com sucesso"}

@api_router.get("/students/{student_id}/justifications", response_model=List[JustificationResponse])
async def get_student_justifications(
    student_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Listar todas as justificativas de um aluno"""
    
    # Verificar permissões
    can_manage = await user_can_manage_student(current_user, student_id)
    if not can_manage:
        raise HTTPException(
            status_code=403,
            detail="Você não tem permissão para ver as justificativas deste aluno"
        )
    
    # Buscar justificativas
    justifications = await db.justifications.find({"student_id": student_id}).to_list(1000)
    
    # Converter para response model
    response_list = []
    for just in justifications:
        response_data = {
            "id": just["id"],
            "student_id": just["student_id"],
            "attendance_id": just.get("attendance_id"),
            "uploaded_by": just["uploaded_by"],
            "uploaded_by_name": just["uploaded_by_name"],
            "uploaded_at": just["uploaded_at"],
            "reason_code": just["reason_code"],
            "reason_text": just.get("reason_text"),
            "file_name": just.get("file_name"),
            "file_mime": just.get("file_mime"),
            "file_size": just.get("file_size"),
            "status": just["status"],
            "visible_to_student": just["visible_to_student"],
            "has_file": bool(just.get("file_id"))
        }
        response_list.append(JustificationResponse(**response_data))
    
    return response_list

@api_router.get("/justifications/{justification_id}/file")
async def get_justification_file(
    justification_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Baixar arquivo de uma justificativa"""
    
    # 1. Buscar justificativa
    justification = await db.justifications.find_one({"id": justification_id})
    if not justification:
        raise HTTPException(status_code=404, detail="Justificativa não encontrada")
    
    # 2. Verificar se tem arquivo
    if not justification.get("file_id"):
        raise HTTPException(status_code=404, detail="Esta justificativa não possui arquivo")
    
    # 3. Verificar permissões
    can_manage = await user_can_manage_student(current_user, justification["student_id"])
    if not can_manage:
        raise HTTPException(
            status_code=403,
            detail="Você não tem permissão para acessar este arquivo"
        )
    
    # 4. Buscar arquivo no GridFS
    try:
        file_id = ObjectId(justification["file_id"])
        grid_out = await fs_bucket.open_download_stream(file_id)
        
        # Ler conteúdo
        contents = await grid_out.read()
        
        # Retornar como streaming response
        return StreamingResponse(
            BytesIO(contents),
            media_type=justification.get("file_mime", "application/octet-stream"),
            headers={
                "Content-Disposition": f'inline; filename="{justification.get("file_name", "arquivo")}"'
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao recuperar arquivo: {str(e)}")

@api_router.delete("/justifications/{justification_id}")
async def delete_justification(
    justification_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Remover uma justificativa (apenas admin ou quem criou)"""
    
    # 1. Buscar justificativa
    justification = await db.justifications.find_one({"id": justification_id})
    if not justification:
        raise HTTPException(status_code=404, detail="Justificativa não encontrada")
    
    # 2. Verificar permissões (admin ou quem criou)
    if current_user.tipo != "admin" and justification["uploaded_by"] != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Apenas admin ou quem criou a justificativa pode removê-la"
        )
    
    # 3. Remover arquivo do GridFS se existir
    if justification.get("file_id"):
        try:
            await fs_bucket.delete(ObjectId(justification["file_id"]))
        except Exception as e:
            print(f"Erro ao remover arquivo do GridFS: {e}")
    
    # 4. Remover justificativa do banco
    await db.justifications.delete_one({"id": justification_id})
    
    # 5. Remover referência da chamada se existir
    if justification.get("attendance_id"):
        student_id = justification["student_id"]
        await db.chamadas.update_one(
            {"id": justification["attendance_id"]},
            {"$unset": {f"presencas.{student_id}.justificado": "", f"presencas.{student_id}.justification_id": ""}}
        )
    
    return {"ok": True, "message": "Justificativa removida com sucesso"}

@api_router.get("/justifications/reasons")
async def get_reason_codes():
    """Listar todos os códigos de motivo disponíveis"""
    return ALLOWED_REASON_CODES

# 🔥 JOB STORAGE SYSTEM - ANTI-TIMEOUT DEFINITIVO
import uuid
import asyncio
from fastapi import BackgroundTasks

# In-memory job storage (use Redis/DB in production)
csv_jobs = {}

@api_router.post("/reports/csv-job")
async def create_csv_job(
    background_tasks: BackgroundTasks,
    turma_id: Optional[str] = None,
    unidade_id: Optional[str] = None,
    curso_id: Optional[str] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    format: CSVFormat = CSVFormat.simple,
    current_user: UserResponse = Depends(get_current_user)
):
    """🚀 Create CSV generation job - NO MORE TIMEOUTS!"""
    job_id = str(uuid.uuid4())
    
    # Store job with status
    csv_jobs[job_id] = {
        "status": "processing",
        "created_at": datetime.now(),
        "user_id": current_user.id,
        "format": format,
        "progress": 0,
        "total_records": 0,
        "csv_url": None,
        "error": None
    }
    
    # Start background job
    background_tasks.add_task(
        generate_csv_background,
        job_id, turma_id, unidade_id, curso_id, data_inicio, data_fim, format, current_user
    )
    
    return {"job_id": job_id, "status": "processing", "message": "CSV generation started"}

@api_router.get("/reports/csv-job/{job_id}")
async def get_csv_job_status(job_id: str, current_user: UserResponse = Depends(get_current_user)):
    """Check CSV job status"""
    if job_id not in csv_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = csv_jobs[job_id]
    
    # Security: only user who created job can access
    if job["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return job

# LEGACY ENDPOINT (kept for compatibility)
@api_router.get("/reports/attendance")
async def get_attendance_report(
    turma_id: Optional[str] = None,
    unidade_id: Optional[str] = None,
    curso_id: Optional[str] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    export_csv: bool = False,
    format: CSVFormat = CSVFormat.simple,
    current_user: UserResponse = Depends(get_current_user)
):
    """⚠️ DEPRECATED: Use POST /reports/csv-job instead for large exports"""
    if export_csv:
        # For small exports, redirect to job system for reliability
        raise HTTPException(
            status_code=410, 
            detail="Use POST /reports/csv-job for CSV exports to avoid timeouts"
        )
    
    # Non-CSV response (JSON) - kept working
    query = {}
    
    # 🔒 FILTROS DE PERMISSÃO POR TIPO DE USUÁRIO
    if current_user.tipo == "instrutor":
        # ✅ Instrutor só pode ver suas turmas REGULARES
        turmas_instrutor = await db.turmas.find({
            "instrutor_id": current_user.id,
            "tipo_turma": "regular"
        }).to_list(1000)
        turmas_ids = [turma["id"] for turma in turmas_instrutor]
        
        if turmas_ids:
            query["turma_id"] = {"$in": turmas_ids}
        else:
            # Se não tem turmas, retorna vazio
            return []
            
    elif current_user.tipo == "pedagogo":
        # ✅ Pedagogo só vê turmas de EXTENSÃO do seu curso/unidade
        turmas_query = {"tipo_turma": "extensao"}
        if getattr(current_user, 'curso_id', None):
            turmas_query["curso_id"] = getattr(current_user, 'curso_id', None)
        if getattr(current_user, 'unidade_id', None):
            turmas_query["unidade_id"] = getattr(current_user, 'unidade_id', None)
            
        turmas_permitidas = await db.turmas.find(turmas_query).to_list(1000)
        turmas_ids = [turma["id"] for turma in turmas_permitidas]
        
        if turmas_ids:
            query["turma_id"] = {"$in": turmas_ids}
        else:
            # Se não tem turmas permitidas, retorna vazio
            return [] if not export_csv else {"csv_data": ""}
    
    elif current_user.tipo == "monitor":
        # Monitor pode ver qualquer tipo de turma do seu curso/unidade
        turmas_query = {}
        if getattr(current_user, 'curso_id', None):
            turmas_query["curso_id"] = getattr(current_user, 'curso_id', None)
        if getattr(current_user, 'unidade_id', None):
            turmas_query["unidade_id"] = getattr(current_user, 'unidade_id', None)
            
        turmas_permitidas = await db.turmas.find(turmas_query).to_list(1000)
        turmas_ids = [turma["id"] for turma in turmas_permitidas]
        
        if turmas_ids:
            query["turma_id"] = {"$in": turmas_ids}
        else:
            # Se não tem turmas permitidas, retorna vazio
            return [] if not export_csv else {"csv_data": ""}
    
    # Filtro por turma específica (aplicado após filtros de permissão)
    if turma_id:
        if "turma_id" in query:
            # Se já há filtro de permissão, verifica se a turma específica está permitida
            if isinstance(query["turma_id"], dict) and "$in" in query["turma_id"]:
                if turma_id not in query["turma_id"]["$in"]:
                    raise HTTPException(status_code=403, detail="Acesso negado a esta turma")
            query["turma_id"] = turma_id
        else:
            query["turma_id"] = turma_id
    
    # Filtros para admin: unidade e curso
    if current_user.tipo == "admin":
        if unidade_id or curso_id:
            # Buscar turmas que atendem aos critérios
            turmas_query = {}
            if unidade_id:
                turmas_query["unidade_id"] = unidade_id
            if curso_id:
                turmas_query["curso_id"] = curso_id
                
            turmas = await db.turmas.find(turmas_query).to_list(1000)
            turmas_ids = [turma["id"] for turma in turmas]
            
            if turmas_ids:
                query["turma_id"] = {"$in": turmas_ids}
            else:
                # Se não há turmas que atendem aos critérios, retorna vazio
                return [] if not export_csv else {"csv_data": ""}
    
    # Filtro por data
    if data_inicio and data_fim:
        query["data"] = {"$gte": data_inicio.isoformat(), "$lte": data_fim.isoformat()}
    elif data_inicio:
        query["data"] = {"$gte": data_inicio.isoformat()}
    elif data_fim:
        query["data"] = {"$lte": data_fim.isoformat()}
    
    # 🎯 CORREÇÃO CRÍTICA: Usar collection 'attendances' (não 'chamadas')
    chamadas = await db.attendances.find(query).to_list(1000)
    
    if export_csv:
        # 🚨 ANTI-TIMEOUT: Use StreamingResponse para evitar 504 Gateway Timeout
        if format == CSVFormat.complete:
            filename = f"relatorio_completo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            return StreamingResponse(
                generate_complete_csv_stream(chamadas),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
        else:  # CSVFormat.simple
            filename = f"relatorio_simples_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            return StreamingResponse(
                generate_simple_csv_stream(chamadas),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
    return [parse_from_mongo(chamada) for chamada in chamadas]


# � STREAMING CSV FUNCTIONS - ANTI-TIMEOUT PROTECTION
async def generate_csv_background(
    job_id: str, turma_id: Optional[str], unidade_id: Optional[str], 
    curso_id: Optional[str], data_inicio: Optional[date], data_fim: Optional[date],
    format: CSVFormat, current_user: UserResponse
):
    """🔥 Background CSV generation - BULLETPROOF AGAINST TIMEOUTS"""
    try:
        import base64
        
        # Update job status
        csv_jobs[job_id]["status"] = "processing"
        csv_jobs[job_id]["progress"] = 10
        
        # Build query with same permissions as original endpoint
        query = {}
        
        # Apply user permissions (simplified for brevity)
        if current_user.tipo == "instrutor":
            turmas_instrutor = await db.turmas.find({
                "instrutor_id": current_user.id,
                "tipo_turma": "regular"
            }).to_list(1000)
            turmas_ids = [turma["id"] for turma in turmas_instrutor]
            if turmas_ids:
                query["turma_id"] = {"$in": turmas_ids}
            else:
                csv_jobs[job_id]["status"] = "completed"
                csv_jobs[job_id]["csv_url"] = "data:text/csv;base64," + base64.b64encode("No data".encode()).decode()
                return
        
        # Apply filters
        if turma_id and current_user.tipo == "admin":
            query["turma_id"] = turma_id
        if data_inicio and data_fim:
            query["data"] = {"$gte": data_inicio.isoformat(), "$lte": data_fim.isoformat()}
        
        # Fetch data
        csv_jobs[job_id]["progress"] = 30
        chamadas = await db.attendances.find(query).to_list(None)
        csv_jobs[job_id]["total_records"] = len(chamadas)
        csv_jobs[job_id]["progress"] = 50
        
        # Generate CSV in memory (safe since background)
        output = StringIO()
        writer = csv.writer(output)
        
        # Simple CSV generation (optimized)
        writer.writerow(["Aluno", "CPF", "Matricula", "Turma", "Data", "Status"])
        
        processed = 0
        for chamada in chamadas:
            try:
                turma = await db.turmas.find_one({"id": chamada.get("turma_id")})
                if not turma:
                    continue
                
                records = chamada.get("records", [])
                for record in records:
                    aluno_id = record.get("aluno_id")
                    if not aluno_id:
                        continue
                    
                    aluno = await db.alunos.find_one({"id": aluno_id})
                    if not aluno:
                        continue
                    
                    writer.writerow([
                        aluno.get("nome", ""),
                        aluno.get("cpf", ""),
                        aluno.get("matricula", aluno.get("id", "")),
                        turma.get("nome", ""),
                        chamada.get("data", ""),
                        "Presente" if record.get("presente", False) else "Ausente"
                    ])
                    processed += 1
                    
                    # Update progress
                    if processed % 100 == 0:
                        progress = 50 + int((processed / (csv_jobs[job_id]["total_records"] * 5)) * 40)
                        csv_jobs[job_id]["progress"] = min(90, progress)
                        
            except Exception as e:
                print(f"Error processing record: {e}")
                continue
        
        # Convert to base64 data URL
        csv_content = output.getvalue()
        csv_base64 = base64.b64encode(csv_content.encode('utf-8')).decode('utf-8')
        
        # Update job with result
        csv_jobs[job_id]["status"] = "completed"
        csv_jobs[job_id]["progress"] = 100
        csv_jobs[job_id]["csv_url"] = f"data:text/csv;charset=utf-8;base64,{csv_base64}"
        csv_jobs[job_id]["completed_at"] = datetime.now()
        
    except Exception as e:
        print(f"❌ Job {job_id} failed: {e}")
        csv_jobs[job_id]["status"] = "failed"
        csv_jobs[job_id]["error"] = str(e)
        csv_jobs[job_id]["progress"] = 0


async def generate_simple_csv_stream(chamadas):
    """Generate simple CSV format with STREAMING - NO MORE 504 TIMEOUTS!"""
    import io
    
    # Initialize buffer
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    
    # Send headers first
    writer.writerow([
        "Aluno", "CPF", "Matricula", "Turma", "Tipo_Turma", "Curso", "Data", 
        "Hora_Inicio", "Hora_Fim", "Status", "Hora_Registro", 
        "Responsavel", "Tipo_Responsavel", "Unidade", "Observacoes"
    ])
    yield buffer.getvalue()
    buffer.seek(0)
    buffer.truncate(0)
    
    # Stream data row by row to prevent memory buildup
    processed = 0
    MAX_SAFE_RECORDS = 10000  # Higher limit since we're streaming
    
    # Process data with STREAMING (sends data as it processes)
    for chamada in chamadas:
        # Safety limit (but much higher since streaming)
        if processed >= MAX_SAFE_RECORDS:
            print(f"⚠️ CSV LIMIT REACHED: {MAX_SAFE_RECORDS} records processed")
            break
            
        try:
            # Buscar dados da turma
            turma = await db.turmas.find_one({"id": chamada.get("turma_id")})
            if not turma:
                continue
            
            # Buscar dados do curso
            curso = await db.cursos.find_one({"id": turma.get("curso_id")}) if turma.get("curso_id") else None
            
            # Buscar dados da unidade
            unidade = await db.unidades.find_one({"id": turma.get("unidade_id")}) if turma.get("unidade_id") else None
            
            # Buscar dados do responsável
            responsavel = await db.usuarios.find_one({"id": turma.get("instrutor_id")}) if turma.get("instrutor_id") else None
            
            # Dados da chamada
            data_chamada = chamada.get("data", "")
            observacoes_gerais = chamada.get("observacoes", "")
            
            # Horários da turma
            hora_inicio = turma.get("horario_inicio", "08:00")
            hora_fim = turma.get("horario_fim", "12:00")
            
            # Records de presença
            records = chamada.get("records", [])
            
            # Para cada aluno na chamada
            for record in records:
                try:
                    aluno_id = record.get("aluno_id")
                    if not aluno_id:
                        continue
                    
                    # Buscar dados do aluno
                    aluno = await db.alunos.find_one({"id": aluno_id})
                    if not aluno:
                        continue
                    
                    # Status
                    presente = record.get("presente", False)
                    justificativa = record.get("justificativa", "")
                    hora_registro = record.get("hora_registro", "")
                    
                    status = "Presente" if presente else "Ausente"
                    
                    # Observações
                    obs_final = []
                    if justificativa:
                        obs_final.append(justificativa)
                    if observacoes_gerais:
                        obs_final.append(f"Obs. turma: {observacoes_gerais}")
                    observacoes_texto = "; ".join(obs_final)
                    
                    # Tipo de turma e responsável
                    tipo_turma = turma.get("tipo_turma", "regular")
                    tipo_turma_label = "Extensão" if tipo_turma == "extensao" else "Regular"
                    
                    tipo_responsavel = responsavel.get("tipo", "instrutor") if responsavel else "instrutor"
                    tipo_responsavel_label = "Pedagogo" if tipo_responsavel == "pedagogo" else "Instrutor"
                    
                    # Write row to buffer and stream immediately
                    writer.writerow([
                        aluno.get("nome", ""),
                        aluno.get("cpf", ""),
                        aluno.get("matricula", aluno.get("id", "")),
                        turma.get("nome", ""),
                        tipo_turma_label,
                        curso.get("nome", "") if curso else "",
                        data_chamada,
                        hora_inicio,
                        hora_fim,
                        status,
                        hora_registro,
                        responsavel.get("nome", "") if responsavel else "",
                        tipo_responsavel_label,
                        unidade.get("nome", "") if unidade else "",
                        observacoes_texto
                    ])
                    
                    # 🚨 STREAM THE ROW IMMEDIATELY (prevents timeout!)
                    yield buffer.getvalue()
                    buffer.seek(0)
                    buffer.truncate(0)
                    
                    processed += 1  # 📊 Count processed records
                    
                except Exception as e:
                    print(f"Erro ao processar record: {e}")
                    continue
                    
        except Exception as e:
            print(f"Erro ao processar chamada {chamada.get('id', 'unknown')}: {e}")
            continue
    
    # Final stream completion
    print(f"✅ CSV Simples concluído: {processed} registros processados")


async def generate_complete_csv_stream(chamadas):
    """Generate complete CSV format with STREAMING - NO MORE TIMEOUTS!"""
    import io
    
    # Initialize buffer
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    
    # Send headers first
    writer.writerow([
        "Nome do Aluno", "CPF", "Data de Nascimento", "Email", "Telefone",
        "Curso", "Tipo de Turma", "Código da Turma", "Unidade", "Ciclo",
        "Instrutor Responsável", "Pedagogo Responsável", "Data de Início", "Data de Término",
        "Total de Chamadas", "Presenças", "Faltas", "% Presença (Total)", "% Presença (Últimos 30 Dias)",
        "Última Chamada Registrada", "Dias Consecutivos de Falta", "Presenças Recentes (Últimas 5 aulas)",
        "Classificação de Risco", "Status do Aluno", "Motivo de Desistência",
        "Média Geral", "Progresso no Curso (%)", "Observações"
    ])
    yield buffer.getvalue()
    buffer.seek(0)
    buffer.truncate(0)
    
    # Calculate student statistics
    student_stats = {}
    MAX_SAFE_RECORDS_COMPLETE = 5000  # Conservative limit for complex processing



    
    # Process all records to build statistics (STREAM-SAFE)
    for chamada in chamadas:
        records = chamada.get("records", [])
        data_chamada = chamada.get("data", "")
        
        for record in records:
            aluno_id = record.get("aluno_id")
            if not aluno_id:
                continue
                
            if aluno_id not in student_stats:
                student_stats[aluno_id] = {
                    "total_chamadas": 0,
                    "presencas": 0,
                    "faltas": 0,
                    "ultima_chamada": "",
                    "faltas_consecutivas": 0,
                    "presencas_recentes": []
                }
            
            student_stats[aluno_id]["total_chamadas"] += 1
            student_stats[aluno_id]["ultima_chamada"] = data_chamada
            
            if record.get("presente", False):
                student_stats[aluno_id]["presencas"] += 1
                student_stats[aluno_id]["faltas_consecutivas"] = 0
            else:
                student_stats[aluno_id]["faltas"] += 1
                student_stats[aluno_id]["faltas_consecutivas"] += 1
    
    # Generate rows for unique students (STREAM EACH ROW)
    processed_students = set()
    processed = 0
    
    for chamada in chamadas:
        try:
            # Buscar dados da turma
            turma = await db.turmas.find_one({"id": chamada.get("turma_id")})
            if not turma:
                continue
            
            # Buscar dados do curso
            curso = await db.cursos.find_one({"id": turma.get("curso_id")}) if turma.get("curso_id") else None
            
            # Buscar dados da unidade
            unidade = await db.unidades.find_one({"id": turma.get("unidade_id")}) if turma.get("unidade_id") else None
            
            # Buscar responsáveis
            instrutor = await db.usuarios.find_one({"id": turma.get("instrutor_id")}) if turma.get("instrutor_id") else None
            
            # Buscar pedagogo (assumindo que está na coleção usuarios com tipo pedagogo)
            pedagogo = await db.usuarios.find_one({
                "tipo": "pedagogo", 
                "unidade_id": turma.get("unidade_id")
            }) if turma.get("unidade_id") else None
            
            # 🚨 TIMEOUT PROTECTION
            if processed >= MAX_SAFE_RECORDS_COMPLETE:
                print(f"⚠️ CSV Completo LIMIT REACHED: {MAX_SAFE_RECORDS_COMPLETE} records")
                break
                
            # Process each student only once
            records = chamada.get("records", [])
            for record in records:
                aluno_id = record.get("aluno_id")
                if not aluno_id or aluno_id in processed_students:
                    continue
                
                processed_students.add(aluno_id)
                
                # Buscar dados completos do aluno
                aluno = await db.alunos.find_one({"id": aluno_id})
                if not aluno:
                    continue
                
                stats = student_stats.get(aluno_id, {})
                
                # Calculate percentages
                total = stats.get("total_chamadas", 0)
                presencas = stats.get("presencas", 0)
                faltas = stats.get("faltas", 0)
                
                perc_total = f"{(presencas/total*100):.1f}%" if total > 0 else "0%"
                perc_30_dias = perc_total  # Simplified for now
                
                # Classification logic
                perc_num = (presencas/total*100) if total > 0 else 0
                if perc_num >= 80:
                    risco = "Baixo"
                elif perc_num >= 60:
                    risco = "Médio"
                else:
                    risco = "Alto"
                
                # Generate enhanced observations
                observacoes = []
                faltas_consecutivas = stats.get("faltas_consecutivas", 0)
                if faltas_consecutivas >= 3:
                    observacoes.append(f"Aluno com {faltas_consecutivas} faltas consecutivas – risco {risco.lower()}")
                elif perc_num == 100:
                    observacoes.append("Excelente frequência e desempenho")
                elif perc_num < 70:
                    observacoes.append("Aluno com baixa frequência e risco alto de evasão")
                
                # Write complete row to buffer
                writer.writerow([
                    aluno.get("nome", ""),  # Nome do Aluno
                    aluno.get("cpf", ""),   # CPF
                    aluno.get("data_nascimento", ""),  # Data de Nascimento
                    aluno.get("email", ""), # Email
                    aluno.get("telefone", ""),  # Telefone
                    curso.get("nome", "") if curso else "",  # Curso
                    "Extensão" if turma.get("tipo_turma") == "extensao" else "Regular",  # Tipo de Turma
                    turma.get("codigo", turma.get("id", "")),  # Código da Turma
                    unidade.get("nome", "") if unidade else "",  # Unidade
                    turma.get("ciclo", ""),  # Ciclo
                    instrutor.get("nome", "") if instrutor else "",  # Instrutor Responsável
                    pedagogo.get("nome", "") if pedagogo else "",   # Pedagogo Responsável
                    turma.get("data_inicio", ""),  # Data de Início
                    turma.get("data_fim", ""),     # Data de Término
                    total,      # Total de Chamadas
                    presencas,  # Presenças
                    faltas,     # Faltas
                    perc_total, # % Presença (Total)
                    perc_30_dias,  # % Presença (Últimos 30 Dias)
                    stats.get("ultima_chamada", ""),  # Última Chamada Registrada
                    faltas_consecutivas,  # Dias Consecutivos de Falta
                    min(presencas, 5),    # Presenças Recentes (simplified)
                    risco,      # Classificação de Risco
                    aluno.get("status", "Ativo"),  # Status do Aluno
                    aluno.get("motivo_desistencia", ""),  # Motivo de Desistência
                    aluno.get("media_geral", ""),  # Média Geral
                    f"{min(100, (presencas/total*100) if total > 0 else 0):.0f}%",  # Progresso no Curso (%)
                    "; ".join(observacoes)  # Observações
                ])
                
                # 🚨 STREAM THE ROW IMMEDIATELY (prevents timeout!)
                yield buffer.getvalue()
                buffer.seek(0)
                buffer.truncate(0)
                
                processed += 1
                
        except Exception as e:
            print(f"Erro ao processar dados completos: {e}")
            continue
    
    # Final stream completion
    print(f"✅ CSV Completo concluído: {processed} registros processados")


# 🔧 LEGACY FUNCTIONS (kept for backward compatibility)
async def generate_simple_csv(chamadas):
    """DEPRECATED: Use generate_simple_csv_stream instead"""
    result = []
    async for chunk in generate_simple_csv_stream(chamadas):
        result.append(chunk)
    return {"csv_data": "".join(result)}


async def generate_complete_csv(chamadas):
    """DEPRECATED: Use generate_complete_csv_stream instead"""
    result = []
    async for chunk in generate_complete_csv_stream(chamadas):
        result.append(chunk)
    return {"csv_data": "".join(result)}

# 📊 NOVO ENDPOINT: CSV de Frequência por Aluno (com estatísticas completas)
@api_router.get("/reports/student-frequency")
async def get_student_frequency_report(
    turma_id: Optional[str] = None,
    unidade_id: Optional[str] = None,
    curso_id: Optional[str] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    export_csv: bool = False,
    current_user: UserResponse = Depends(get_current_user)
):
    """Gerar relatório de frequência por aluno com estatísticas completas"""
    
    # 🔒 Aplicar filtros de permissão por tipo de usuário (mesmo código do endpoint anterior)
    query = {}
    
    if current_user.tipo == "instrutor":
        turmas_instrutor = await db.turmas.find({
            "instrutor_id": current_user.id,
            "tipo_turma": "regular"
        }).to_list(1000)
        turmas_ids = [turma["id"] for turma in turmas_instrutor]
        
        if turmas_ids:
            query["turma_id"] = {"$in": turmas_ids}
        else:
            return [] if not export_csv else {"csv_data": ""}
            
    elif current_user.tipo == "pedagogo":
        turmas_query = {"tipo_turma": "extensao"}
        if getattr(current_user, 'curso_id', None):
            turmas_query["curso_id"] = getattr(current_user, 'curso_id', None)
        if getattr(current_user, 'unidade_id', None):
            turmas_query["unidade_id"] = getattr(current_user, 'unidade_id', None)
            
        turmas_permitidas = await db.turmas.find(turmas_query).to_list(1000)
        turmas_ids = [turma["id"] for turma in turmas_permitidas]
        
        if turmas_ids:
            query["turma_id"] = {"$in": turmas_ids}
        else:
            return [] if not export_csv else {"csv_data": ""}
    
    elif current_user.tipo == "monitor":
        turmas_query = {}
        if getattr(current_user, 'curso_id', None):
            turmas_query["curso_id"] = getattr(current_user, 'curso_id', None)
        if getattr(current_user, 'unidade_id', None):
            turmas_query["unidade_id"] = getattr(current_user, 'unidade_id', None)
            
        turmas_permitidas = await db.turmas.find(turmas_query).to_list(1000)
        turmas_ids = [turma["id"] for turma in turmas_permitidas]
        
        if turmas_ids:
            query["turma_id"] = {"$in": turmas_ids}
        else:
            return [] if not export_csv else {"csv_data": ""}

    # Filtros administrativos (para admin)
    if current_user.tipo == "admin":
        if unidade_id or curso_id:
            turmas_query = {}
            if unidade_id:
                turmas_query["unidade_id"] = unidade_id
            if curso_id:
                turmas_query["curso_id"] = curso_id
                
            turmas = await db.turmas.find(turmas_query).to_list(1000)
            turmas_ids = [turma["id"] for turma in turmas]
            
            if turmas_ids:
                query["turma_id"] = {"$in": turmas_ids}
            else:
                return [] if not export_csv else {"csv_data": ""}

    # Filtro por turma específica
    if turma_id:
        if "turma_id" in query:
            if isinstance(query["turma_id"], dict) and "$in" in query["turma_id"]:
                if turma_id not in query["turma_id"]["$in"]:
                    raise HTTPException(status_code=403, detail="Acesso negado a esta turma")
            query["turma_id"] = turma_id
        else:
            query["turma_id"] = turma_id

    # Filtro por data
    if data_inicio and data_fim:
        query["data"] = {"$gte": data_inicio.isoformat(), "$lte": data_fim.isoformat()}
    elif data_inicio:
        query["data"] = {"$gte": data_inicio.isoformat()}
    elif data_fim:
        query["data"] = {"$lte": data_fim.isoformat()}

    # Buscar todas as attendances
    attendances = await db.attendances.find(query).to_list(1000)
    
    if export_csv:
        # 📊 CALCULAR ESTATÍSTICAS POR ALUNO
        aluno_stats = {}
        
        # Processar cada attendance
        for attendance in attendances:
            turma_id = attendance.get("turma_id")
            records = attendance.get("records", [])
            
            for record in records:
                aluno_id = record.get("aluno_id")
                presente = record.get("presente", False)
                
                if aluno_id not in aluno_stats:
                    aluno_stats[aluno_id] = {
                        "total_chamadas": 0,
                        "total_presencas": 0,
                        "total_faltas": 0,
                        "turma_id": turma_id  # Para buscar dados da turma depois
                    }
                
                aluno_stats[aluno_id]["total_chamadas"] += 1
                if presente:
                    aluno_stats[aluno_id]["total_presencas"] += 1
                else:
                    aluno_stats[aluno_id]["total_faltas"] += 1
        
        # Gerar CSV
        output = StringIO()
        writer = csv.writer(output)
        
        # Cabeçalhos conforme a imagem
        writer.writerow([
            "Nome do Aluno", "CPF", "Total de Chamadas", "Presencas", "Faltas", 
            "% Presença (Preciso)", "Classificação de Risco", "Status do Aluno", 
            "Data de Nascimento", "Email"
        ])
        
        # Processar cada aluno
        for aluno_id, stats in aluno_stats.items():
            try:
                # Buscar dados do aluno
                aluno = await db.alunos.find_one({"id": aluno_id})
                if not aluno:
                    continue
                
                # Calcular percentual preciso
                total_chamadas = stats["total_chamadas"]
                total_presencas = stats["total_presencas"]
                percentual = round((total_presencas / total_chamadas * 100), 2) if total_chamadas > 0 else 0.0
                
                # Classificação de risco
                if percentual >= 75:
                    risco = "Situação Normal"
                elif percentual >= 50:
                    risco = "Atenção"
                else:
                    risco = "Situação Crítica"
                
                # Formatar data de nascimento
                data_nasc = aluno.get("data_nascimento")
                if data_nasc:
                    if isinstance(data_nasc, str):
                        data_nasc_str = data_nasc
                    else:
                        data_nasc_str = data_nasc.strftime("%d/%m/%Y") if hasattr(data_nasc, 'strftime') else str(data_nasc)
                else:
                    data_nasc_str = "N/A"
                
                # Escrever linha
                writer.writerow([
                    aluno.get("nome", ""),
                    aluno.get("cpf", ""),
                    stats["total_chamadas"],
                    stats["total_presencas"],
                    stats["total_faltas"],
                    f"{percentual:.2f}%",
                    risco,
                    aluno.get("status", "ativo").title(),
                    data_nasc_str,
                    aluno.get("email", "N/A")
                ])
                
            except Exception as e:
                print(f"Erro ao processar aluno {aluno_id}: {e}")
                continue
        
        output.seek(0)
        return {"csv_data": output.getvalue()}
    
    # Se não for export_csv, retorna dados estruturados
    return {"message": "Use export_csv=true para baixar CSV"}

# � Função auxiliar para verificar dias de aula
def eh_dia_de_aula(data_verificar: date, dias_aula: List[str]) -> bool:
    """Verifica se uma data específica é dia de aula baseado na configuração do curso"""
    dias_semana = {
        0: "segunda",
        1: "terca", 
        2: "quarta",
        3: "quinta", 
        4: "sexta",
        5: "sabado",
        6: "domingo"
    }
    
    dia_da_semana = data_verificar.weekday()
    nome_dia = dias_semana.get(dia_da_semana, "")
    
    return nome_dia in dias_aula

# �🚨 SISTEMA DE NOTIFICAÇÕES - Chamadas Pendentes (Personalizado por Curso)
@api_router.get("/notifications/pending-calls")
async def get_pending_calls(current_user: UserResponse = Depends(get_current_user)):
    """Verificar chamadas não realizadas baseado nos dias de aula do curso"""
    
    # Data atual
    hoje = date.today()
    ontem = hoje - timedelta(days=1)
    anteontem = hoje - timedelta(days=2)
    
    # Query para turmas baseado no tipo de usuário
    query_turmas = {"ativo": True}
    
    if current_user.tipo == "instrutor":
        query_turmas["instrutor_id"] = current_user.id
    elif current_user.tipo in ["pedagogo", "monitor"]:
        if getattr(current_user, 'curso_id', None):
            query_turmas["curso_id"] = getattr(current_user, 'curso_id', None)
        if getattr(current_user, 'unidade_id', None):
            query_turmas["unidade_id"] = getattr(current_user, 'unidade_id', None)
    # Admin vê todas as turmas
    
    turmas = await db.turmas.find(query_turmas).to_list(1000)
    chamadas_pendentes = []
    
    for turma in turmas:
        try:
            # 📅 Buscar dados do curso para verificar dias de aula
            curso = await db.cursos.find_one({"id": turma.get("curso_id")})
            dias_aula = curso.get("dias_aula", ["segunda", "terca", "quarta", "quinta"]) if curso else ["segunda", "terca", "quarta", "quinta"]
            
            # Buscar dados do instrutor, unidade e curso
            instrutor = await db.usuarios.find_one({"id": turma.get("instrutor_id")}) if turma.get("instrutor_id") else None
            unidade = await db.unidades.find_one({"id": turma.get("unidade_id")}) if turma.get("unidade_id") else None
            
            instrutor_nome = instrutor.get("nome", "Instrutor não encontrado") if instrutor else "Sem instrutor"
            unidade_nome = unidade.get("nome", "Unidade não encontrada") if unidade else "Sem unidade"
            curso_nome = curso.get("nome", "Curso não encontrado") if curso else "Sem curso"
            
            # 📅 HOJE: Verificar se hoje é dia de aula e se tem chamada
            if eh_dia_de_aula(hoje, dias_aula):
                # 🎯 CORREÇÃO CRÍTICA: Usar collection 'attendances' (não 'chamadas')
                chamada_hoje = await db.attendances.find_one({
                    "turma_id": turma["id"],
                    "data": hoje.isoformat()
                })
                
                if not chamada_hoje:
                    chamadas_pendentes.append({
                        "turma_id": turma["id"],
                        "turma_nome": turma["nome"],
                        "instrutor_id": turma.get("instrutor_id"),
                        "instrutor_nome": instrutor_nome,
                        "unidade_nome": unidade_nome,
                        "curso_nome": curso_nome,
                        "data_faltante": hoje.isoformat(),
                        "prioridade": "alta",
                        "motivo": f"Chamada não realizada hoje ({hoje.strftime('%d/%m/%Y')})",
                        "dias_aula": dias_aula
                    })
            
            # 📅 ONTEM: Verificar se ontem era dia de aula e se tem chamada
            if eh_dia_de_aula(ontem, dias_aula):
                # 🎯 CORREÇÃO CRÍTICA: Usar collection 'attendances' (não 'chamadas')
                chamada_ontem = await db.attendances.find_one({
                    "turma_id": turma["id"],
                    "data": ontem.isoformat()
                })
                
                if not chamada_ontem:
                    chamadas_pendentes.append({
                        "turma_id": turma["id"],
                        "turma_nome": turma["nome"],
                        "instrutor_id": turma.get("instrutor_id"),
                        "instrutor_nome": instrutor_nome,
                        "unidade_nome": unidade_nome,
                        "curso_nome": curso_nome,
                        "data_faltante": ontem.isoformat(),
                        "prioridade": "media",
                        "motivo": f"Chamada não realizada ontem ({ontem.strftime('%d/%m/%Y')})",
                        "dias_aula": dias_aula
                    })
            
            # 📅 ANTEONTEM: Verificar se anteontem era dia de aula e se tem chamada
            if eh_dia_de_aula(anteontem, dias_aula):
                # 🎯 CORREÇÃO CRÍTICA: Usar collection 'attendances' (não 'chamadas')
                chamada_anteontem = await db.attendances.find_one({
                    "turma_id": turma["id"],
                    "data": anteontem.isoformat()
                })
                
                if not chamada_anteontem:
                    chamadas_pendentes.append({
                        "turma_id": turma["id"],
                        "turma_nome": turma["nome"],
                        "instrutor_id": turma.get("instrutor_id"),
                        "instrutor_nome": instrutor_nome,
                        "unidade_nome": unidade_nome,
                        "curso_nome": curso_nome,
                        "data_faltante": anteontem.isoformat(),
                        "prioridade": "baixa",
                        "motivo": f"Chamada não realizada em {anteontem.strftime('%d/%m/%Y')}",
                        "dias_aula": dias_aula
                    })
                    
        except Exception as e:
            print(f"Erro ao processar turma {turma.get('id', 'unknown')}: {e}")
            continue
    
    return {
        "total_pendentes": len(chamadas_pendentes),
        "chamadas_pendentes": chamadas_pendentes,
        "data_verificacao": hoje.isoformat()
    }

# 📊 DASHBOARD PERSONALIZADO POR USUÁRIO
@api_router.get("/dashboard/stats")
async def get_dashboard_stats(current_user: UserResponse = Depends(get_current_user)):
    hoje = date.today()
    primeiro_mes = hoje.replace(day=1)
    
    if current_user.tipo == "admin":
        # 👑 ADMIN: Visão geral completa
        total_unidades = await db.unidades.count_documents({"ativo": True})
        total_cursos = await db.cursos.count_documents({"ativo": True})
        
        # 🔧 CORREÇÃO CRÍTICA: Contar alunos únicos corretamente
        all_alunos = await db.alunos.find({}).to_list(10000)
        alunos_ativos = len([a for a in all_alunos if a.get("status") == "ativo"])
        alunos_desistentes = len([a for a in all_alunos if a.get("status") == "desistente"])
        total_alunos = alunos_ativos + alunos_desistentes
        
        total_turmas = await db.turmas.count_documents({"ativo": True})
        
        print(f"🔧 DASHBOARD ADMIN: {total_alunos} alunos únicos ({alunos_ativos} ativos + {alunos_desistentes} desistentes)")
        
        # 🎯 CORRIGIR: Usar collection 'attendances' (não 'chamadas')
        chamadas_hoje = await db.attendances.count_documents({"data": hoje.isoformat()})
        
        # Stats mensais
        chamadas_mes = await db.attendances.find({"data": {"$gte": primeiro_mes.isoformat()}}).to_list(1000)
        
        # 🎯 CORRIGIR: Calcular presenças e faltas a partir dos records
        total_presencas_mes = 0
        total_faltas_mes = 0
        
        for chamada in chamadas_mes:
            records = chamada.get("records", [])
            presentes = len([r for r in records if r.get("presente", False)])
            ausentes = len(records) - presentes
            total_presencas_mes += presentes
            total_faltas_mes += ausentes
        
        return {
            "total_unidades": total_unidades,
            "total_cursos": total_cursos,
            "total_alunos": total_alunos,
            "total_turmas": total_turmas,
            "alunos_ativos": alunos_ativos,
            "alunos_desistentes": alunos_desistentes,
            "chamadas_hoje": chamadas_hoje,
            "presencas_mes": total_presencas_mes,
            "faltas_mes": total_faltas_mes,
            "taxa_presenca_mes": round((total_presencas_mes / (total_presencas_mes + total_faltas_mes) * 100) if (total_presencas_mes + total_faltas_mes) > 0 else 0, 1)
        }
    
    elif current_user.tipo == "instrutor":
        # 👨‍🏫 INSTRUTOR: Apenas suas turmas para estatísticas de chamada
        minhas_turmas = await db.turmas.find({"instrutor_id": current_user.id, "ativo": True}).to_list(1000)
        turmas_ids = [turma["id"] for turma in minhas_turmas]
        
        # � ALUNOS ATIVOS: TODOS DO CURSO (não apenas das turmas do instrutor)
        if getattr(current_user, 'curso_id', None):
            # Buscar TODAS as turmas do curso (não só do instrutor)
            todas_turmas_curso = await db.turmas.find({
                "curso_id": getattr(current_user, 'curso_id', None),
                "ativo": True
            }).to_list(1000)
            
            # Coletar IDs únicos de TODOS os alunos do curso
            alunos_unicos_curso = set()
            for turma in todas_turmas_curso:
                for aluno_id in turma.get("alunos_ids", []):
                    alunos_unicos_curso.add(aluno_id)
            
            # 🎯 CONTAR APENAS ALUNOS DO CURSO (alternativa por problema com $in)
            alunos_ativos = 0
            alunos_desistentes = 0
            
            if alunos_unicos_curso:
                # ALTERNATIVA: Usar aggregation pipeline para contornar problema $in
                pipeline_ativos = [
                    {"$match": {"id": {"$in": list(alunos_unicos_curso)}, "status": "ativo"}},
                    {"$count": "total"}
                ]
                
                pipeline_desistentes = [
                    {"$match": {"id": {"$in": list(alunos_unicos_curso)}, "status": "desistente"}},
                    {"$count": "total"}
                ]
                
                result_ativos = await db.alunos.aggregate(pipeline_ativos).to_list(1)
                result_desistentes = await db.alunos.aggregate(pipeline_desistentes).to_list(1)
                
                alunos_ativos = result_ativos[0]["total"] if result_ativos else 0
                alunos_desistentes = result_desistentes[0]["total"] if result_desistentes else 0
        else:
            # Fallback se não tiver curso_id definido
            alunos_ativos = 0
            alunos_desistentes = 0
        
        # 🎯 CORRIGIR: Chamadas do instrutor usando collection 'attendances'
        chamadas_hoje = await db.attendances.count_documents({
            "turma_id": {"$in": turmas_ids},
            "data": hoje.isoformat()
        })
        
        # Stats mensais das suas turmas
        chamadas_mes = await db.attendances.find({
            "turma_id": {"$in": turmas_ids},
            "data": {"$gte": primeiro_mes.isoformat()}
        }).to_list(1000)
        
        # 🎯 CORRIGIR: Calcular presenças e faltas a partir dos records
        total_presencas_mes = 0
        total_faltas_mes = 0
        
        for chamada in chamadas_mes:
            records = chamada.get("records", [])
            presentes = len([r for r in records if r.get("presente", False)])
            ausentes = len(records) - presentes
            total_presencas_mes += presentes
            total_faltas_mes += ausentes
        
        # Buscar dados do curso do instrutor
        curso_nome = "Seu Curso"
        unidade_nome = "Sua Unidade"
        
        if getattr(current_user, 'curso_id', None):
            curso = await db.cursos.find_one({"id": getattr(current_user, 'curso_id', None)})
            if curso:
                curso_nome = curso.get("nome", "Seu Curso")
        
        if getattr(current_user, 'unidade_id', None):
            unidade = await db.unidades.find_one({"id": getattr(current_user, 'unidade_id', None)})
            if unidade:
                unidade_nome = unidade.get("nome", "Sua Unidade")
        
        return {
            "total_unidades": 1,  # Sua unidade
            "total_cursos": 1,    # Seu curso
            "total_alunos": alunos_ativos + alunos_desistentes,  # Total baseado nos status
            "total_turmas": len(minhas_turmas),
            "alunos_ativos": alunos_ativos,
            "alunos_desistentes": alunos_desistentes,
            "chamadas_hoje": chamadas_hoje,
            "presencas_mes": total_presencas_mes,
            "faltas_mes": total_faltas_mes,
            "taxa_presenca_mes": round((total_presencas_mes / (total_presencas_mes + total_faltas_mes) * 100) if (total_presencas_mes + total_faltas_mes) > 0 else 0, 1),
            "curso_nome": curso_nome,
            "unidade_nome": unidade_nome,
            "tipo_usuario": "Instrutor"
        }
    
    elif current_user.tipo in ["pedagogo", "monitor"]:
        # 👩‍🎓 PEDAGOGO/MONITOR: Turmas do seu curso/unidade
        query_turmas = {"ativo": True}
        if getattr(current_user, 'curso_id', None):
            query_turmas["curso_id"] = getattr(current_user, 'curso_id', None)
        if getattr(current_user, 'unidade_id', None):
            query_turmas["unidade_id"] = getattr(current_user, 'unidade_id', None)
        
        turmas_permitidas = await db.turmas.find(query_turmas).to_list(1000)
        turmas_ids = [turma["id"] for turma in turmas_permitidas]
        
        # 🔄 CONTAR ALUNOS ÚNICOS (SEM DUPLICAÇÃO)
        alunos_unicos = set()
        for turma in turmas_permitidas:
            for aluno_id in turma.get("alunos_ids", []):
                alunos_unicos.add(aluno_id)
        
        # Buscar status apenas dos alunos únicos
        alunos_ativos = 0
        alunos_desistentes = 0
        
        if alunos_unicos:
            alunos_lista = await db.alunos.find({"id": {"$in": list(alunos_unicos)}}).to_list(1000)
            for aluno in alunos_lista:
                if aluno.get("status") == "ativo":
                    alunos_ativos += 1
                elif aluno.get("status") == "desistente":
                    alunos_desistentes += 1
        
        # 🎯 CORRIGIR: Chamadas das turmas permitidas usando collection 'attendances'
        chamadas_hoje = await db.attendances.count_documents({
            "turma_id": {"$in": turmas_ids},
            "data": hoje.isoformat()
        })
        
        # Stats mensais
        chamadas_mes = await db.attendances.find({
            "turma_id": {"$in": turmas_ids},
            "data": {"$gte": primeiro_mes.isoformat()}
        }).to_list(1000)
        
        total_presencas_mes = sum(c.get("total_presentes", 0) for c in chamadas_mes)
        total_faltas_mes = sum(c.get("total_faltas", 0) for c in chamadas_mes)
        
        # Buscar dados do curso/unidade
        curso_nome = "Seu Curso"
        unidade_nome = "Sua Unidade"
        
        if getattr(current_user, 'curso_id', None):
            curso = await db.cursos.find_one({"id": getattr(current_user, 'curso_id', None)})
            if curso:
                curso_nome = curso.get("nome", "Seu Curso")
        
        if getattr(current_user, 'unidade_id', None):
            unidade = await db.unidades.find_one({"id": getattr(current_user, 'unidade_id', None)})
            if unidade:
                unidade_nome = unidade.get("nome", "Sua Unidade")
        
        return {
            "total_unidades": 1,  # Sua unidade
            "total_cursos": 1,    # Seu curso
            "total_alunos": len(alunos_unicos),
            "total_turmas": len(turmas_permitidas),
            "alunos_ativos": alunos_ativos,
            "alunos_desistentes": alunos_desistentes,
            "chamadas_hoje": chamadas_hoje,
            "presencas_mes": total_presencas_mes,
            "faltas_mes": total_faltas_mes,
            "taxa_presenca_mes": round((total_presencas_mes / (total_presencas_mes + total_faltas_mes) * 100) if (total_presencas_mes + total_faltas_mes) > 0 else 0, 1),
            "curso_nome": curso_nome,
            "unidade_nome": unidade_nome,
            "tipo_usuario": current_user.tipo.title()
        }

# MIGRAÇÃO DE DADOS - Corrigir alunos sem data_nascimento
@api_router.post("/migrate/fix-students")
async def fix_students_migration(current_user: UserResponse = Depends(get_current_user)):
    """🔧 MIGRAÇÃO: Adiciona data_nascimento padrão para alunos existentes"""
    check_admin_permission(current_user)
    
    try:
        # Buscar alunos sem data_nascimento
        alunos_sem_data = await db.alunos.find({
            "$or": [
                {"data_nascimento": {"$exists": False}},
                {"data_nascimento": None}
            ]
        }).to_list(1000)
        
        if not alunos_sem_data:
            return {"message": "Todos os alunos já possuem data_nascimento", "migrated": 0}
        
        # Atualizar com data padrão (1 de janeiro de 2000)
        data_padrao = date(2000, 1, 1)
        migrated_count = 0
        
        for aluno in alunos_sem_data:
            await db.alunos.update_one(
                {"id": aluno["id"]},
                {"$set": {"data_nascimento": data_padrao.isoformat()}}
            )
            migrated_count += 1
        
        return {
            "message": f"Migração concluída! {migrated_count} alunos atualizados",
            "migrated": migrated_count,
            "data_padrao_usada": data_padrao.isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na migração: {str(e)}")

# 🔄 MIGRAÇÃO: Adicionar tipo_turma em turmas existentes
async def migrate_turmas_tipo():
    """Migração para adicionar campo tipo_turma em turmas existentes"""
    try:
        print("🔄 Iniciando migração de turmas...")
        
        # Buscar turmas sem o campo tipo_turma
        turmas_sem_tipo = await db.turmas.find({"tipo_turma": {"$exists": False}}).to_list(1000)
        
        if not turmas_sem_tipo:
            print("✅ Nenhuma migração necessária - todas as turmas já têm tipo_turma")
            return
        
        print(f"🔄 Migrando {len(turmas_sem_tipo)} turmas...")
        
        for turma in turmas_sem_tipo:
            # Buscar o responsável da turma
            responsavel = await db.usuarios.find_one({"id": turma.get("instrutor_id")})
            
            # Determinar tipo baseado no responsável
            if responsavel and responsavel.get("tipo") == "pedagogo":
                tipo_turma = "extensao"
            else:
                tipo_turma = "regular"  # Default para instrutor ou admin
            
            # Atualizar turma
            await db.turmas.update_one(
                {"id": turma["id"]},
                {"$set": {"tipo_turma": tipo_turma}}
            )
            
            print(f"✅ Turma '{turma.get('nome', 'sem nome')}' → {tipo_turma}")
        
        print(f"✅ Migração concluída: {len(turmas_sem_tipo)} turmas atualizadas")
        
    except Exception as e:
        print(f"❌ Erro na migração de turmas: {e}")

# Endpoint manual para migração
@api_router.post("/migrate/turmas-tipo")
async def migrate_turmas_tipo_endpoint(current_user: UserResponse = Depends(get_current_user)):
    """Endpoint manual para migração de tipo_turma"""
    if current_user.tipo != "admin":
        raise HTTPException(status_code=403, detail="Apenas admin pode executar migrações")
    
    await migrate_turmas_tipo()
    return {"message": "Migração de tipo_turma executada com sucesso"}

# 🎯 PRODUÇÃO: Sistema de inicialização removido - sem dados de exemplo

# 🎯 PRODUÇÃO: Função de criação de dados de exemplo removida

# RELATÓRIOS DINÂMICOS - ENDPOINT COMPLETO
@api_router.get("/reports/teacher-stats")
async def get_dynamic_teacher_stats(
    unidade_id: Optional[str] = None,
    curso_id: Optional[str] = None,
    turma_id: Optional[str] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    current_user: UserResponse = Depends(get_current_user)
):
    """📊 RELATÓRIOS DINÂMICOS: Estatísticas completas e atualizadas automaticamente com filtros para admin"""
    if current_user.tipo not in ["instrutor", "pedagogo", "monitor", "admin"]:
        raise HTTPException(status_code=403, detail="Acesso restrito")
    
    # 🎯 Filtrar turmas baseado no tipo de usuário e filtros
    query_turmas = {"ativo": True}
    
    if current_user.tipo == "admin":
        # Admin pode usar filtros
        if unidade_id:
            query_turmas["unidade_id"] = unidade_id
        if curso_id:
            query_turmas["curso_id"] = curso_id
        if turma_id:
            query_turmas["id"] = turma_id
    elif current_user.tipo == "instrutor":
        # ✅ Instrutor: apenas turmas REGULARES que ele instrui
        query_turmas["instrutor_id"] = current_user.id
        query_turmas["tipo_turma"] = "regular"
    elif current_user.tipo == "pedagogo":
        # ✅ Pedagogo: apenas turmas de EXTENSÃO da sua unidade/curso
        if getattr(current_user, 'curso_id', None):
            query_turmas["curso_id"] = getattr(current_user, 'curso_id', None)
        if getattr(current_user, 'unidade_id', None):
            query_turmas["unidade_id"] = getattr(current_user, 'unidade_id', None)
        query_turmas["tipo_turma"] = "extensao"
    elif current_user.tipo == "monitor":
        # Monitor: pode ver qualquer tipo de turma que monitora
        if getattr(current_user, 'curso_id', None):
            query_turmas["curso_id"] = getattr(current_user, 'curso_id', None)
        if getattr(current_user, 'unidade_id', None):
            query_turmas["unidade_id"] = getattr(current_user, 'unidade_id', None)
    
    # 📈 Buscar turmas do usuário
    turmas = await db.turmas.find(query_turmas).to_list(1000)
    turma_ids = [turma["id"] for turma in turmas]
    
    # 🔍 DEBUG: Log para debugar desistentes
    print(f"📊 STATS DEBUG - Usuário: {current_user.nome} ({current_user.tipo})")
    print(f"   📝 Query turmas: {query_turmas}")
    print(f"   🎯 Turmas encontradas: {len(turmas)}")
    for turma in turmas:
        print(f"      • {turma['nome']} (ID: {turma['id']}) - Alunos: {len(turma.get('alunos_ids', []))}")
    
    if not turma_ids:
        return {
            "taxa_media_presenca": 0,
            "total_alunos": 0,
            "alunos_em_risco": 0,
            "desistentes": 0,
            "maiores_presencas": [],
            "maiores_faltas": [],
            "resumo_turmas": []
        }
    
    # 📊 Calcular estatísticas dinâmicas por aluno
    alunos_stats = []
    for turma in turmas:
        aluno_ids = turma.get("alunos_ids", [])
        if not aluno_ids:
            continue
            
        # Buscar alunos da turma
        alunos = await db.alunos.find({"id": {"$in": aluno_ids}}).to_list(1000)
        
        for aluno in alunos:
            # Contar presenças e faltas do aluno nesta turma com filtro de data
            query_chamadas = {"turma_id": turma["id"]}
            
            # Aplicar filtro de data se fornecido
            if data_inicio and data_fim:
                query_chamadas["data"] = {"$gte": data_inicio.isoformat(), "$lte": data_fim.isoformat()}
            elif data_inicio:
                query_chamadas["data"] = {"$gte": data_inicio.isoformat()}
            elif data_fim:
                query_chamadas["data"] = {"$lte": data_fim.isoformat()}
            
            # 🎯 CORREÇÃO CRÍTICA: Usar collection 'attendances' (não 'chamadas')
            chamadas = await db.attendances.find(query_chamadas).to_list(1000)
            
            total_aulas = len(chamadas)
            presencas = 0
            faltas = 0
            
            for chamada in chamadas:
                # ✅ CORREÇÃO: Usar 'records' em vez de 'presencas'
                records = chamada.get("records", [])
                for record in records:
                    if record.get("aluno_id") == aluno["id"]:
                        if record.get("presente", False):
                            presencas += 1
                        else:
                            faltas += 1
            
            if total_aulas > 0:
                taxa_presenca = (presencas / total_aulas) * 100
            else:
                taxa_presenca = 0
            
            alunos_stats.append({
                "id": aluno["id"],
                "nome": aluno["nome"],
                "turma": turma["nome"],
                "presencas": presencas,
                "faltas": faltas,
                "total_aulas": total_aulas,
                "taxa_presenca": round(taxa_presenca, 1),
                "status": aluno.get("status", "ativo")
            })
    
    # 📊 Calcular métricas gerais - APENAS ALUNOS ATIVOS
    alunos_ativos_stats = [a for a in alunos_stats if a["status"] == "ativo"]
    
    # 🔍 DEBUG: Log detalhado de alunos
    print(f"   📈 Total alunos processados: {len(alunos_stats)}")
    print(f"   ✅ Alunos ativos: {len(alunos_ativos_stats)}")
    
    # Debug por status
    status_count = {}
    for aluno in alunos_stats:
        status = aluno["status"]
        status_count[status] = status_count.get(status, 0) + 1
        if status == "desistente":
            print(f"      🚫 Desistente encontrado: {aluno['nome']} (Turma: {aluno['turma']})")
    
    print(f"   📊 Status breakdown: {status_count}")
    
    # 🔧 CORREÇÃO CRÍTICA: Contar alunos únicos (não duplicados entre turmas)
    alunos_unicos = {}
    desistentes_unicos = {}
    
    for aluno in alunos_stats:
        aluno_id = aluno["id"]
        if aluno["status"] == "ativo":
            if aluno_id not in alunos_unicos:
                alunos_unicos[aluno_id] = aluno
            else:
                # Se já existe, manter o que tem melhor taxa de presença ou maior número de aulas
                existing = alunos_unicos[aluno_id]
                if aluno["total_aulas"] > existing["total_aulas"]:
                    alunos_unicos[aluno_id] = aluno
        elif aluno["status"] == "desistente":
            if aluno_id not in desistentes_unicos:
                desistentes_unicos[aluno_id] = aluno
    
    # Usar apenas alunos únicos para cálculos
    alunos_unicos_list = list(alunos_unicos.values())
    
    if alunos_unicos_list:
        # 🎯 CORREÇÃO: Taxa média baseada em alunos únicos
        taxa_media = sum(a["taxa_presenca"] for a in alunos_unicos_list) / len(alunos_unicos_list)
        
        # 🎯 CORREÇÃO: Alunos em risco baseado em alunos únicos
        alunos_em_risco_unicos = [a for a in alunos_unicos_list if a["taxa_presenca"] < 75]
        
        print(f"   🎯 RESULTADO: {len(desistentes_unicos)} desistentes únicos calculados")
        print(f"   🎯 CORREÇÃO: Taxa média recalculada: {round(taxa_media, 1)}%")
        print(f"   🎯 CORREÇÃO: Alunos em risco únicos: {len(alunos_em_risco_unicos)}")
        
        # Top 3 maiores presenças - APENAS ALUNOS ÚNICOS
        maiores_presencas = sorted(alunos_unicos_list, key=lambda x: x["taxa_presenca"], reverse=True)[:3]
        
        # ✅ CORREÇÃO: Top 3 maiores faltas ordenado por número de faltas - ALUNOS ÚNICOS
        maiores_faltas = sorted(alunos_unicos_list, key=lambda x: x["faltas"], reverse=True)[:3]
    else:
        taxa_media = 0
        alunos_em_risco_unicos = []
        maiores_presencas = []
        maiores_faltas = []
    
    # 📋 Resumo por turma
    resumo_turmas = []
    for turma in turmas:
        turma_alunos = [a for a in alunos_stats if a["turma"] == turma["nome"]]
        if turma_alunos:
            media_turma = sum(a["taxa_presenca"] for a in turma_alunos) / len(turma_alunos)
        else:
            media_turma = 0
            
        resumo_turmas.append({
            "nome": turma["nome"],
            "total_alunos": len(turma_alunos),
            "taxa_media": round(media_turma, 1),
            "alunos_risco": len([a for a in turma_alunos if a["taxa_presenca"] < 75])
        })
    
    total_alunos_correto = len(alunos_unicos)
    total_desistentes_correto = len(desistentes_unicos)
    
    print(f"   🎯 CORREÇÃO FINAL: Total alunos únicos: {total_alunos_correto} (antes: {len(alunos_stats)})")
    print(f"   🎯 CORREÇÃO FINAL: Total desistentes únicos: {total_desistentes_correto}")
    
    return {
        "taxa_media_presenca": f"{round(taxa_media, 1)}%",
        "total_alunos": total_alunos_correto,  # 🔧 CORRIGIDO: Contagem única
        "alunos_em_risco": len(alunos_em_risco_unicos),  # 🔧 CORRIGIDO: Baseado em alunos únicos
        "desistentes": total_desistentes_correto,  # 🔧 CORRIGIDO: Contagem única
        "alunos_desistentes": total_desistentes_correto,  # ✅ CORRIGIDO: Compatibilidade com frontend
        "maiores_presencas": [
            {
                "nome": a["nome"],
                "turma": a["turma"],
                "taxa_presenca": f"{a['taxa_presenca']}%",
                "aulas_presentes": f"{a['presencas']}/{a['total_aulas']} aulas"
            } for a in maiores_presencas
        ],
        "maiores_faltas": [
            {
                "nome": a["nome"],
                "turma": a["turma"],
                "taxa_presenca": f"{a['taxa_presenca']}%",
                "faltas": f"{a['faltas']}/{a['total_aulas']} faltas"
            } for a in maiores_faltas
        ],
        "resumo_turmas": resumo_turmas
    }

# TEACHER STATS ENDPOINT - CORRIGIDO PARA PEDAGOGO/INSTRUTOR
# ENDPOINT REMOVIDO - DUPLICADO

# 🚀 NOVOS ENDPOINTS PARA SISTEMA DE CHAMADAS PENDENTES

@api_router.get("/instructor/me/pending-attendances", response_model=PendingAttendancesResponse)
async def get_pending_attendances_for_instructor(current_user: UserResponse = Depends(get_current_user)):
    """
    🎯 RBAC - Lista chamadas pendentes baseado no tipo de usuário:
    - ADMIN: Todas as chamadas pendentes do sistema
    - INSTRUTOR: Apenas suas turmas
    - PEDAGOGO: Turmas da sua unidade/curso
    - MONITOR: Turmas que monitora
    
    🗓️ REGRAS DE DIAS: Considera apenas dias de aula programados (seg-sex + cursos específicos)
    - Segunda a Sexta: Padrão para todos os cursos
    - Sábado: Apenas cursos específicos que têm aula
    - Domingo: Nenhuma aula
    - Sexta: Nem sempre (conforme programação do curso)
    """
    
    hoje = today_iso_date()
    
    try:
        print(f"🔍 [DEBUG] Buscando chamadas pendentes para {current_user.email} (tipo: {current_user.tipo})")
        
        # Converter hoje para objeto date para comparação
        hoje_date = datetime.fromisoformat(hoje).date()
        print(f"🔍 [DEBUG] Data hoje: {hoje_date}")
        
        # 🎯 RBAC - Filtrar turmas baseado no tipo de usuário
        if current_user.tipo == "admin":
            # 👑 ADMIN: Ver todas as turmas ativas do sistema
            cursor = db.turmas.find({"ativo": True})
            print(f"🔍 [DEBUG] Admin - buscando todas as turmas ativas")
            
        elif current_user.tipo == "instrutor":
            # 🧑‍🏫 INSTRUTOR: Apenas suas turmas
            cursor = db.turmas.find({
                "instrutor_id": current_user.id,
                "ativo": True
            })
            print(f"🔍 [DEBUG] Instrutor - buscando turmas do instrutor_id: {current_user.id}")
            
        elif current_user.tipo == "pedagogo":
            # 👩‍🎓 PEDAGOGO: Turmas da sua unidade/curso
            query_turmas = {"ativo": True}
            if getattr(current_user, 'curso_id', None):
                query_turmas["curso_id"] = getattr(current_user, 'curso_id', None)
            if getattr(current_user, 'unidade_id', None):
                query_turmas["unidade_id"] = getattr(current_user, 'unidade_id', None)
            cursor = db.turmas.find(query_turmas)
            
        elif current_user.tipo == "monitor":
            # 👨‍💻 MONITOR: Turmas que ele monitora (mesmo critério do pedagogo)
            query_turmas = {"ativo": True}
            if getattr(current_user, 'curso_id', None):
                query_turmas["curso_id"] = getattr(current_user, 'curso_id', None)
            if getattr(current_user, 'unidade_id', None):
                query_turmas["unidade_id"] = getattr(current_user, 'unidade_id', None)
            cursor = db.turmas.find(query_turmas)
            
        else:
            raise HTTPException(status_code=403, detail="Tipo de usuário não autorizado")
        
        turmas = await cursor.to_list(length=1000)
        print(f"🔍 [DEBUG] Encontradas {len(turmas)} turmas")
        pending = []
        
        # 🚀 LÓGICA DE CHAMADAS PENDENTES: Verificar baseado nos dias de aula
        
        for t in turmas:
            tid = t.get("id")
            turma_nome = t.get("nome", "Turma sem nome")
            curso_id = t.get("curso_id")
            
            # 🎯 BUSCAR DIAS DA SEMANA DO CURSO (NÃO DA TURMA!)
            dias_semana = []
            if curso_id:
                curso = await db.cursos.find_one({"id": curso_id})
                if curso:
                    dias_semana = curso.get("dias_semana", [])
            
            # Se o curso não tem dias específicos, usar dias úteis como padrão (segunda=0 a sexta=4)
            if not dias_semana:
                dias_semana = [0, 1, 2, 3, 4]  # Segunda a Sexta
                
            # 📅 VERIFICAR PERÍODO DA TURMA
            data_inicio = t.get("data_inicio")
            data_fim = t.get("data_fim")
            
            # Converter strings para date se necessário
            if isinstance(data_inicio, str):
                data_inicio = datetime.fromisoformat(data_inicio).date()
            if isinstance(data_fim, str):
                data_fim = datetime.fromisoformat(data_fim).date()
            
            # 🎯 VERIFICAR APENAS HOJE E ONTEM (máximo 2 dias atrás)
            # Não mostrar chamadas muito antigas para evitar confusão
            for dias_atras in range(3):  # 0 = hoje, 1 = ontem, 2 = anteontem
                data_verificar = hoje_date - timedelta(days=dias_atras)
                data_iso = data_verificar.isoformat()
                
                # 🎯 FILTROS IMPORTANTES:
                
                # 1) Verificar se está no período da turma
                if data_inicio and data_fim:
                    if not (data_inicio <= data_verificar <= data_fim):
                        continue  # Data fora do período da turma
                
                # 2) Verificar se é dia de aula (baseado em dias_semana do curso)
                dia_semana = data_verificar.weekday()  # 0=segunda, 6=domingo
                if dia_semana not in dias_semana:
                    continue  # Não é dia de aula programado
                
                # Verificar se já existe attendance para esta data
                att = await db.attendances.find_one({"turma_id": tid, "data": data_iso})
                
                if not att:  # Não tem attendance = pendente
                    # Buscar dados básicos dos alunos da turma
                    alunos_ids = t.get("alunos_ids", [])
                    if alunos_ids:
                        # CORREÇÃO: Usar collection 'alunos' que é a correta no sistema
                        alunos_cursor = db.alunos.find(
                            {"id": {"$in": alunos_ids}}, 
                            {"id": 1, "nome": 1}
                        )
                        alunos = await alunos_cursor.to_list(1000)
                    else:
                        alunos = []
                    
                    # Determinar prioridade baseada na data
                    if dias_atras == 0:
                        prioridade = "urgente"  # Hoje
                        status_msg = f"Chamada não realizada hoje ({data_iso})"
                    elif dias_atras == 1:
                        prioridade = "importante"  # Ontem
                        status_msg = f"Chamada não realizada ontem ({data_iso})"
                    else:
                        prioridade = "pendente"  # Dias anteriores
                        status_msg = f"Chamada não realizada em {data_iso}"
                    
                    pending.append({
                        "turma_id": tid,
                        "turma_nome": turma_nome,
                        "data_pendente": data_iso,
                        "dias_atras": dias_atras,
                        "prioridade": prioridade,
                        "status_msg": status_msg,
                        "alunos": [{"id": a.get("id"), "nome": a.get("nome")} for a in alunos],
                        "vagas": t.get("vagas_total", 0),
                        "horario": f"{t.get('horario_inicio', '')}-{t.get('horario_fim', '')}"
                    })
        
        # Ordenar por prioridade: urgente -> importante -> pendente, depois por data (mais recente primeiro)
        prioridade_ordem = {"urgente": 0, "importante": 1, "pendente": 2}
        pending.sort(key=lambda x: (prioridade_ordem.get(x["prioridade"], 3), x["dias_atras"]))
        
        print(f"🔍 [DEBUG] Retornando {len(pending)} chamadas pendentes")
        return PendingAttendancesResponse(date=hoje, pending=pending)
        
    except Exception as e:
        print(f"❌ Erro ao buscar chamadas pendentes: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@api_router.get("/classes/{turma_id}/attendance/today")
async def get_attendance_today(turma_id: str, current_user: UserResponse = Depends(get_current_user)):
    """Verificar se já existe chamada para turma hoje"""
    hoje = today_iso_date()
    
    # Validar permissão: instrutor dono da turma ou admin
    # CORREÇÃO: Usar collection 'turmas' que é a correta no sistema
    turma = await db.turmas.find_one({"id": turma_id})
    if not turma:
        raise HTTPException(404, "Turma não encontrada")
    
    if current_user.tipo == "instrutor" and turma.get("instrutor_id") != current_user.id:
        raise HTTPException(403, "Acesso negado - turma não pertence ao instrutor")
    
    att = await db.attendances.find_one({"turma_id": turma_id, "data": hoje})
    if not att:
        raise HTTPException(status_code=204, detail="Nenhuma chamada para hoje")
    
    # Serializar para resposta
    return AttendanceResponse(
        id=att.get("id", str(att.get("_id"))),
        turma_id=att["turma_id"],
        data=att["data"],
        created_by=att["created_by"],
        created_at=att["created_at"],
        records=att.get("records", []),
        observacao=att.get("observacao")
    )

@api_router.post("/classes/{turma_id}/attendance/{data_chamada}", status_code=201)
async def create_attendance_for_date(
    turma_id: str,
    data_chamada: str,  # Data no formato YYYY-MM-DD
    payload: AttendanceCreate, 
    current_user: UserResponse = Depends(get_current_user)
):
    """Criar chamada para data específica (permite chamadas retroativas - única ação, imutável)"""
    
    # Validar formato da data
    try:
        data_obj = datetime.fromisoformat(data_chamada).date()
        data_iso = data_obj.isoformat()
    except ValueError:
        raise HTTPException(400, "Data inválida. Use formato YYYY-MM-DD")
    
    # Validar que a data não é futura
    hoje = datetime.now().date()
    if data_obj > hoje:
        raise HTTPException(400, "Não é possível registrar chamadas para datas futuras")
    
    # Validações
    # CORREÇÃO: Usar collection 'turmas' que é a correta no sistema
    turma = await db.turmas.find_one({"id": turma_id})
    if not turma:
        raise HTTPException(404, "Turma não encontrada")
    
    # Permissões: só instrutor da turma ou admin
    if current_user.tipo == "instrutor" and turma.get("instrutor_id") != current_user.id:
        raise HTTPException(403, "Acesso negado - turma não pertence ao instrutor")
    
    # Montar documento
    doc = {
        "id": str(uuid.uuid4()),
        "turma_id": turma_id,
        "data": data_iso,  # Usar a data específica
        "records": [r.dict() for r in payload.records],
        "observacao": payload.observacao,
        "created_by": current_user.id,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    try:
        # Inserir com chave única (turma_id, data)
        # IMPORTANTE: Criar índice único no MongoDB primeiro!
        res = await db.attendances.insert_one(doc)
        
        # Log para auditoria
        print(f"✅ Chamada criada: turma={turma_id}, data={data_iso}, by={current_user.id}")
        
        return {
            "id": doc["id"],
            "message": "Chamada salva com sucesso",
            "data": data_iso,
            "turma_id": turma_id
        }
        
    except DuplicateKeyError:
        # Já existe uma chamada para essa turma/data
        print(f"⚠️ Tentativa de criar chamada duplicada: turma={turma_id}, data={data_iso}")
        raise HTTPException(
            status_code=409, 
            detail=f"Chamada do dia {data_iso} já existe e não pode ser alterada"
        )
    except Exception as e:
        print(f"❌ Erro ao salvar chamada: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno ao salvar chamada: {str(e)}")

@api_router.post("/classes/{turma_id}/attendance/today", status_code=201)
async def create_attendance_today(
    turma_id: str, 
    payload: AttendanceCreate, 
    current_user: UserResponse = Depends(get_current_user)
):
    """Criar chamada de hoje (wrapper para compatibilidade)"""
    hoje = today_iso_date()
    return await create_attendance_for_date(turma_id, hoje, payload, current_user)

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=[
        "http://localhost:3000",  # Desenvolvimento local
        "https://front-end-sistema-qbl0lhxig-jesielamarojunior-makers-projects.vercel.app",  # Vercel deployment
        "https://front-end-sistema.vercel.app",  # Vercel custom domain
        "https://sistema-ios-frontend.vercel.app",  # Possível domínio personalizado
        "*"  # Fallback para desenvolvimento
    ],
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 🚀 PING ENDPOINT - WAKE UP RENDER
@app.get("/ping")
async def ping_server():
    """Endpoint para acordar o servidor Render"""
    return {
        "status": "alive",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "message": "Backend está funcionando!",
        "cors_test": "OK"
    }

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

# Railway compatibility - run server if executed directly
@api_router.get("/teacher/stats")
async def get_teacher_stats(current_user: dict = Depends(get_current_user)):
    """✅ CORRIGIDO: Estatísticas por tipo de usuário com cálculos corretos"""
    try:
        # 🎯 FILTRAR DADOS BASEADO NO TIPO DE USUÁRIO
        if current_user["tipo"] == "admin":
            # Admin: todas as turmas e chamadas
            query_turmas = {"ativo": True}
            query_chamadas = {}
            query_alunos = {}
        elif current_user["tipo"] == "instrutor":
            # ✅ Instrutor: apenas suas turmas REGULARES
            query_turmas = {"instrutor_id": current_user["id"], "ativo": True, "tipo_turma": "regular"}
        elif current_user["tipo"] == "pedagogo":
            # ✅ Pedagogo: apenas turmas de EXTENSÃO da unidade/curso
            query_turmas = {"ativo": True, "tipo_turma": "extensao"}
            if current_user.get("unidade_id"):
                query_turmas["unidade_id"] = current_user["unidade_id"]
            if current_user.get("curso_id"):
                query_turmas["curso_id"] = current_user["curso_id"]
        elif current_user["tipo"] == "monitor":
            # Monitor: turmas que monitora
            query_turmas = {"monitor_id": current_user["id"], "ativo": True}
        else:
            # Tipo desconhecido
            query_turmas = {}
        
        # 📊 BUSCAR TURMAS DO USUÁRIO
        turmas = await db.turmas.find(query_turmas).to_list(1000)
        turma_ids = [turma["id"] for turma in turmas]
        
        if not turma_ids and current_user["tipo"] != "admin":
            # Usuário sem turmas: retornar dados zerados
            return {
                "taxa_media_presenca": "0.0%",
                "total_alunos": 0,
                "alunos_em_risco": 0,
                "desistentes": 0,
                "chamadas_hoje": 0,
                "total_turmas": 0,
                "ultima_atualizacao": datetime.now().isoformat()
            }
        
        # 📅 FILTRAR CHAMADAS POR TURMAS DO USUÁRIO
        if current_user["tipo"] == "admin":
            query_chamadas = {}
        else:
            query_chamadas = {"turma_id": {"$in": turma_ids}}
            
        todas_chamadas = await db.attendances.find(query_chamadas).to_list(1000)
        
        # 🧮 CÁLCULOS DE PRESENÇA
        total_presentes = 0
        total_registros = 0
        alunos_stats = {}
        
        for chamada in todas_chamadas:
            records = chamada.get('records', [])
            for record in records:
                aluno_id = record.get('aluno_id')
                presente = record.get('presente', False)
                
                total_registros += 1
                if presente:
                    total_presentes += 1
                
                # Stats por aluno
                if aluno_id not in alunos_stats:
                    alunos_stats[aluno_id] = {'presentes': 0, 'faltas': 0}
                
                if presente:
                    alunos_stats[aluno_id]['presentes'] += 1
                else:
                    alunos_stats[aluno_id]['faltas'] += 1
        
        # ✅ TAXA DE PRESENÇA REAL
        taxa_presenca = (total_presentes / total_registros * 100) if total_registros > 0 else 0
        
        # 🚨 ALUNOS EM RISCO (mais de 25% faltas)
        alunos_risco = 0
        for stats in alunos_stats.values():
            total_aulas = stats['presentes'] + stats['faltas']
            if total_aulas > 0 and (stats['faltas'] / total_aulas) > 0.25:
                alunos_risco += 1
        
        # 👥 CONTAR ALUNOS ÚNICOS DAS TURMAS DO USUÁRIO
        alunos_unicos = set()
        for turma in turmas:
            alunos_ids = turma.get("alunos_ids", [])
            alunos_unicos.update(alunos_ids)
        total_alunos_usuario = len(alunos_unicos)
        
        # 📊 FILTRAR DESISTENTES POR ESCOPO DO USUÁRIO
        if current_user["tipo"] == "admin":
            desistentes = await db.alunos.count_documents({"status": "desistente"})
        else:
            # ✅ CORREÇÃO: Desistentes apenas dos alunos das turmas do usuário (com tipo de turma)
            alunos_ids_list = list(alunos_unicos)
            if alunos_ids_list:
                # Buscar alunos desistentes que estão nas turmas do usuário
                desistentes = await db.alunos.count_documents({
                    "id": {"$in": alunos_ids_list},
                    "status": "desistente"
                })
                print(f"🔍 DEBUG Desistentes {current_user['tipo']}: {desistentes} alunos desistentes de {len(alunos_ids_list)} alunos totais")
            else:
                desistentes = 0
        
        # 📅 CHAMADAS DE HOJE
        hoje = date.today().isoformat()
        if current_user["tipo"] == "admin":
            chamadas_hoje = await db.attendances.count_documents({"data": hoje})
        else:
            chamadas_hoje = await db.attendances.count_documents({
                "turma_id": {"$in": turma_ids},
                "data": hoje
            }) if turma_ids else 0
        
        print(f"📊 STATS {current_user['tipo'].upper()}: {taxa_presenca:.1f}% ({total_presentes}/{total_registros}) - Turmas: {len(turmas)}")
        
        return {
            "taxa_media_presenca": f"{taxa_presenca:.1f}%",
            "total_alunos": total_alunos_usuario,
            "alunos_em_risco": alunos_risco,
            "desistentes": desistentes,
            "chamadas_hoje": chamadas_hoje,
            "total_turmas": len(turmas),
            "total_presentes": total_presentes,
            "total_faltas": total_registros - total_presentes,
            "usuario_tipo": current_user["tipo"],
            "ultima_atualizacao": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Erro teacher/stats: {e}")
        return {
            "taxa_media_presenca": "0.0%",
            "total_alunos": 0,
            "alunos_em_risco": 0,
            "desistentes": 0,
            "chamadas_hoje": 0,
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=False)