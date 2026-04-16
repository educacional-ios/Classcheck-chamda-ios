
Conteúdo colado
331.90 KB •8.981 linhas
•
A formatação pode estar inconsistente com a fonte
  // ClassCheck - Sistema de Chamada IOS (v1.1)
  import React, { useState, useEffect } from "react";
  import "./App.css";
  import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
  import axios from "axios";
  import { Button } from "./components/ui/button";
  import { Input } from "./components/ui/input";
  import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
  } from "./components/ui/card";
  import { Label } from "./components/ui/label";
  import { Badge } from "./components/ui/badge";
  import { Tabs, TabsContent, TabsList, TabsTrigger } from "./components/ui/tabs";
  import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
  } from "./components/ui/dialog";
  import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
  } from "./components/ui/select";
  import { Textarea } from "./components/ui/textarea";
  import { Checkbox } from "./components/ui/checkbox";
  import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
  } from "./components/ui/table";
  import { useToast } from "./hooks/use-toast";
  import { Toaster } from "./components/ui/toaster";
  import {
    Users,
    GraduationCap,
    Building2,
    BookOpen,
    UserCheck,
    UserX,
    FileText,
    AlertCircle,
    Calendar,
    Upload,
    Download,
    LogOut,
    Plus,
    Eye,
    EyeOff,
    Edit,
    Trash2,
    Key,
    TrendingUp,
    TrendingDown,
    CheckCircle,
    Phone,
    Mail,
    MapPin,
    Clock,
    Save,
    UserPlus,
    Shield,
    BarChart3,
    Copy,
    RefreshCw,
    Info,
    Filter,
    Search,
    X,
    Bell,
    BellRing,
    AlertTriangle,
    TriangleAlert,
    Lock,
  } from "lucide-react";
  
  const BACKEND_URL =
    process.env.REACT_APP_BACKEND_URL ||
    "https://sistema-ios-backend.onrender.com";
  const API = `${BACKEND_URL}/api`;
  
  // 🔍 SISTEMA DE DEBUG UNIVERSAL - Para testar em outros computadores
  const DEBUG_MODE = localStorage.getItem("ios_debug") === "true";
  
  const debugLog = (message, data = null) => {
    if (DEBUG_MODE || process.env.NODE_ENV === "development") {
      const timestamp = new Date().toISOString();
      console.log(`[${timestamp}] IOS DEBUG:`, message, data || "");
  
      // Salvar log no localStorage para análise posterior
      const logs = JSON.parse(localStorage.getItem("ios_debug_logs") || "[]");
      logs.push({ timestamp, message, data });
      if (logs.length > 100) logs.shift(); // Manter apenas últimos 100 logs
      localStorage.setItem("ios_debug_logs", JSON.stringify(logs));
    }
  };
  
  // 🚨 CAPTURADOR DE ERROS GLOBAIS DO REACT DOM
  window.addEventListener("error", (event) => {
    debugLog("ERRO GLOBAL CAPTURADO", {
      message: event.message,
      filename: event.filename,
      lineno: event.lineno,
      colno: event.colno,
      stack: event.error?.stack,
    });
  
    // Verificar se é o erro específico do removeChild
    if (
      event.message.includes("removeChild") ||
      event.message.includes("NotFoundError")
    ) {
      debugLog("ERRO REACT DOM removeChild DETECTADO", {
        message: event.message,
        userAgent: navigator.userAgent,
        url: window.location.href,
      });
    }
  });
  
  window.addEventListener("unhandledrejection", (event) => {
    debugLog("PROMISE REJEITADA NÃO TRATADA", {
      reason: event.reason,
      stack: event.reason?.stack,
    });
  });
  
  // Configurar timeout global para axios
  axios.defaults.timeout = 30000; // Aumentado para 30 segundos (Fase 2)
  
  // 🔄 INTERCEPTOR COM RETRY - FASE 2 (Correção de Timeout)
  axios.interceptors.response.use(
    (response) => response,
    async (error) => {
      const config = error.config;
      if (!config || !config.retry) config.retry = 0;
        
      if (
              config.retry < 3 &&
              (error.code === "ECONNABORTED" || error.name === "AxiosError") &&
              !error.response
            ) {
        config.retry += 1;
        console.log(`🔄 Tentativa ${config.retry}/3 para ${config.url}`);
        return axios(config);
      }
  
      // Log estruturado do erro
      console.error("❌ Erro na requisição:", {
        url: config?.url,
        method: config?.method,
        error: error.message,
        status: error.response?.status,
      });
  
      return Promise.reject(error);
    },
  );
  
  // � REGRAS DE NEGÓCIO - FASE 3 (Precisão dos Cálculos)
  const REGRAS_PRESENCA = {
    MINIMO_APROVACAO: 75, // % mínimo para aprovação
    EM_RISCO: 60, // 60-74% = Aluno em risco
    CRITICO: 40, // < 60% = Situação crítica
    ALERTA_FALTAS_CONSECUTIVAS: 3, // 3+ faltas seguidas = alerta
    PERIODO_ANALISE_TENDENCIA: 30, // Dias para análise preditiva
    INCLUIR_DESISTENTES_STATS: false, // Não contar desistentes nas médias
  };
  
  // 🎯 CLASSIFICADOR DE RISCO DE ALUNO
  const classificarRiscoAluno = (percentualPresenca) => {
    if (percentualPresenca >= REGRAS_PRESENCA.MINIMO_APROVACAO) return "adequado";
    if (percentualPresenca >= REGRAS_PRESENCA.EM_RISCO) return "em_risco";
    return "critico";
  };
  
  // 📈 CALCULADORA DE ESTATÍSTICAS PRECISAS
  const calcularEstatisticasPrecisas = (alunos, chamadas) => {
    const alunosAtivos = REGRAS_PRESENCA.INCLUIR_DESISTENTES_STATS
      ? alunos
      : alunos.filter((aluno) => aluno.status !== "desistente");
  
    const totalAlunos = alunosAtivos.length;
  
    if (totalAlunos === 0)
      return {
        totalAlunos: 0,
        alunosEmRisco: 0,
        desistentes: alunos.filter((a) => a.status === "desistente").length,
        taxaMediaPresenca: 0,
      };
  
    // Calcular presença por aluno
    const estatisticasPorAluno = alunosAtivos.map((aluno) => {
      const chamadasAluno = chamadas.filter((c) => c.aluno_id === aluno.id);
      const totalChamadas = chamadasAluno.length;
      const presencas = chamadasAluno.filter((c) => c.presente).length;
      const percentual =
        totalChamadas > 0 ? (presencas / totalChamadas) * 100 : 0;
  
      return {
        ...aluno,
        totalChamadas,
        presencas,
        percentualPresenca: percentual,
        classificacao: classificarRiscoAluno(percentual),
      };
    });
  
    // Estatísticas gerais
    const alunosEmRisco = estatisticasPorAluno.filter(
      (a) => a.classificacao === "em_risco" || a.classificacao === "critico",
    ).length;
  
    const taxaMediaPresenca =
      estatisticasPorAluno.length > 0
        ? estatisticasPorAluno.reduce(
            (acc, aluno) => acc + aluno.percentualPresenca,
            0,
          ) / estatisticasPorAluno.length
        : 0;
  
    return {
      totalAlunos,
      alunosEmRisco,
      desistentes: alunos.filter((a) => a.status === "desistente").length,
      taxaMediaPresenca: Math.round(taxaMediaPresenca * 100) / 100,
      estatisticasPorAluno,
    };
  };
  
  // 👥 NOMENCLATURA UNISSEX - OUT/2024 (Fase 1)
    const getUserTypeLabel = (tipo) => {
      const labels = {
        admin: "Administrador(a)",
        instrutor: "Professor(a)",
        pedagogo: "Educador Social",
        monitor: "Monitor(a)",
        gestor: "Gestor(a)",
      };
      return labels[tipo] || tipo;
    };
  
  // 📊 GERADOR CSV COM DADOS PRECISOS - FASE 4
  const gerarCSVComDadosPrecisos = (estatisticasPrecisas, filtrosAplicados) => {
    console.log("🔧 Gerando CSV com dados precisos Fase 4");
  
    // 📋 CABEÇALHO APRIMORADO COM NOVOS CAMPOS
    const headers = [
      "Nome do Aluno",
      "CPF",
      "Total de Chamadas",
      "Presenças",
      "Faltas",
      "% Presença (Preciso)",
      "Classificação de Risco",
      "Status do Aluno",
      "Data de Nascimento",
      "Email",
      "Telefone",
      "Observações",
    ];
  
    // 📊 PROCESSAR DADOS COM CÁLCULOS PRECISOS
    const linhas = estatisticasPrecisas.estatisticasPorAluno.map((aluno) => {
      const faltas = aluno.totalChamadas - aluno.presencas;
  
      // 🎯 Traduzir classificação para texto legível
      const classificacaoTexto =
        {
          adequado: "Frequência Adequada",
          em_risco: "Aluno em Risco",
          critico: "Situação Crítica",
        }[aluno.classificacao] || "Não Classificado";
  
      // 🎯 Status traduzido
      const statusTexto =
        {
          ativo: "Ativo",
          desistente: "Desistente",
          concluido: "Concluído",
        }[aluno.status] || "Ativo";
  
      return [
        aluno.nome_social || aluno.nome,
        aluno.cpf || "N/A",
        aluno.totalChamadas.toString(),
        aluno.presencas.toString(),
        faltas.toString(),
        `${aluno.percentualPresenca.toFixed(2)}%`, // PRECISÃO DE 2 CASAS
        classificacaoTexto,
        statusTexto,
        aluno.data_nascimento || "N/A",
        aluno.email || "N/A",
        aluno.telefone || "N/A",
        aluno.observacoes || "",
      ];
    });
  
    // 📈 RODAPÉ COM ESTATÍSTICAS GERAIS
    const rodape = [
      [""],
      ["=== ESTATÍSTICAS GERAIS (FASE 3) ==="],
      [`Total de Alunos Ativos: ${estatisticasPrecisas.totalAlunos}`],
      [`Alunos em Risco: ${estatisticasPrecisas.alunosEmRisco}`],
      [`Desistentes: ${estatisticasPrecisas.desistentes}`],
      [
        `Taxa Média de Presença: ${estatisticasPrecisas.taxaMediaPresenca.toFixed(
          2,
        )}%`,
      ],
      [""],
      ["=== REGRAS APLICADAS ==="],
      [`Mínimo para Aprovação: ≥${REGRAS_PRESENCA.MINIMO_APROVACAO}%`],
      [
        `Alerta de Risco: ${REGRAS_PRESENCA.EM_RISCO}% - ${
          REGRAS_PRESENCA.MINIMO_APROVACAO - 1
        }%`,
      ],
      [`Situação Crítica: <${REGRAS_PRESENCA.EM_RISCO}%`],
      [
        `Desistentes nas médias: ${
          REGRAS_PRESENCA.INCLUIR_DESISTENTES_STATS ? "SIM" : "NÃO"
        }`,
      ],
      [""],
      [`Relatório gerado em: ${new Date().toLocaleString("pt-BR")}`],
      [`Sistema: IOS - Fase 4 (Cálculos Precisos)`],
    ];
  
    // 🔄 CONVERTER PARA CSV
    const todasLinhas = [headers, ...linhas, ...rodape];
    const csvContent = todasLinhas
      .map((linha) =>
        linha
          .map((campo) => `"${campo.toString().replace(/"/g, '""')}"`)
          .join(","),
      )
      .join("\n");
  
    // 📋 ADICIONAR BOM (Byte Order Mark) para UTF-8
    const csvComBOM = "\ufeff" + csvContent;
  
    console.log(
      `✅ CSV gerado: ${linhas.length} alunos, ${headers.length} colunas`,
    );
    return csvComBOM;
  };
  
  // 🔧 HEALTH CHECK SISTEMA - FASE 5
  const verificarHealthSistema = async (alunosData = [], chamadasData = []) => {
    console.log("🔍 Executando Health Check - Fase 5");
  
    const healthStatus = {
      timestamp: new Date().toISOString(),
      versao_sistema: "IOS v2.0 - Fase 5",
      fases_ativas: [],
      backend_status: "unknown",
      frontend_status: "ok",
      dados_disponiveis: false,
      calculos_precisos: false,
      csv_funcionando: false,
      estatisticas: {},
    };
  
    try {
      // 🎯 TESTAR CONECTIVIDADE BACKEND
      try {
        const pingResponse = await axios.get(`${API}/ping`, { timeout: 5000 });
        healthStatus.backend_status = "ok";
        healthStatus.backend_response_time =
          pingResponse.config.timeout || "< 5s";
      } catch (backendError) {
        console.warn("⚠️ Backend offline, continuando em modo local");
        healthStatus.backend_status = "offline";
        healthStatus.modo_offline = true;
      }
  
      // 🎯 VERIFICAR DADOS LOCAIS
      if (alunosData && alunosData.length > 0) {
        healthStatus.dados_disponiveis = true;
        healthStatus.total_alunos = alunosData.length;
        healthStatus.total_chamadas = chamadasData ? chamadasData.length : 0;
  
        // Testar cálculos precisos da Fase 3
        try {
          const testeCalculo = calcularEstatisticasPrecisas(
            alunosData.slice(0, 5),
            chamadasData || [],
          );
          healthStatus.calculos_precisos = true;
          healthStatus.fases_ativas.push("Fase 3 - Cálculos Precisos");
          healthStatus.estatisticas.taxa_media = testeCalculo.taxaMediaPresenca;
          healthStatus.estatisticas.alunos_em_risco = testeCalculo.alunosEmRisco;
        } catch (calculoError) {
          console.error("❌ Erro nos cálculos Fase 3:", calculoError);
          healthStatus.calculos_precisos = false;
        }
  
        // Testar geração CSV da Fase 4
        try {
          const testeCsv = gerarCSVComDadosPrecisos(
            {
              estatisticasPorAluno: alunosData.slice(0, 2).map((a) => ({
                ...a,
                totalChamadas: 10,
                presencas: 8,
                percentualPresenca: 80,
                classificacao: "adequado",
              })),
              totalAlunos: 2,
              alunosEmRisco: 0,
              desistentes: 0,
              taxaMediaPresenca: 80,
            },
            {},
          );
          healthStatus.csv_funcionando = testeCsv.length > 100;
          if (healthStatus.csv_funcionando) {
            healthStatus.fases_ativas.push("Fase 4 - CSV Aprimorado");
          }
        } catch (csvError) {
          console.error("❌ Erro na geração CSV Fase 4:", csvError);
          healthStatus.csv_funcionando = false;
        }
      }
  
      // 🎯 VERIFICAR FASES IMPLEMENTADAS
      if (typeof REGRAS_PRESENCA !== "undefined") {
        healthStatus.fases_ativas.push("Fase 3 - Regras de Negócio");
      }
      if (typeof getUserTypeLabel !== "undefined") {
        healthStatus.fases_ativas.push("Fase 1 - Nomenclatura Unissex");
      }
  
      healthStatus.fases_ativas.push("Fase 5 - Health Check");
  
      // 🎯 STATUS GERAL
      healthStatus.status_geral =
        healthStatus.backend_status === "ok" &&
        healthStatus.dados_disponiveis &&
        healthStatus.calculos_precisos
          ? "saudavel"
          : "alerta";
  
      console.log("✅ Health Check concluído:", healthStatus);
      return healthStatus;
    } catch (error) {
      console.error("❌ Erro no Health Check:", error);
      healthStatus.status_geral = "erro";
      healthStatus.erro = error.message;
      return healthStatus;
    }
  };
  
  // ErrorBoundary para capturar erros do React
  class ErrorBoundary extends React.Component {
    constructor(props) {
      super(props);
      this.state = { hasError: false };
    }
  
    static getDerivedStateFromError(error) {
      return { hasError: true };
    }
  
    componentDidCatch(error, errorInfo) {
      console.error("ErrorBoundary capturou erro:", error, errorInfo);
    }
  
    render() {
      if (this.state.hasError) {
        return (
          <div style={{ padding: "20px", textAlign: "center" }}>
            <h2>Algo deu errado</h2>
            <button onClick={() => window.location.reload()}>
              Recarregar página
            </button>
          </div>
        );
      }
  
      return this.props.children;
    }
  }
  
  // Authentication Context
  const AuthContext = React.createContext();
  
  const useAuth = () => {
    const context = React.useContext(AuthContext);
    if (!context) {
      throw new Error("useAuth must be used within an AuthProvider");
    }
    return context;
  };
  
  const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(localStorage.getItem("token"));
    const [loading, setLoading] = useState(true);
    const isMounted = React.useRef(true);
  
    useEffect(() => {
      isMounted.current = true;
      return () => {
        isMounted.current = false;
      };
    }, []);
  
    useEffect(() => {
      console.log("🚀 Inicializando autenticação...");
      console.log("🔗 Backend URL:", BACKEND_URL);
  
      if (!BACKEND_URL) {
        console.error("❌ BACKEND_URL não configurado!");
        setLoading(false);
        return;
      }
  
      if (token) {
        console.log("🔑 Token encontrado, verificando usuário...");
        axios.defaults.headers.common["Authorization"] = `Bearer ${token}`;
        fetchCurrentUser();
      } else {
        console.log("ℹ️ Sem token, direcionando para login");
        setLoading(false);
      }
    }, [token]);
  
    const fetchCurrentUser = async () => {
      try {
        console.log("🔍 Verificando usuário atual...");
        const response = await axios.get(`${API}/auth/me`);
        console.log("✅ Usuário carregado:", response.data.email);
        if (isMounted.current) {
          setUser(response.data);
        }
      } catch (error) {
        console.error("❌ Erro ao buscar usuário:", error);
        // Limpar dados inválidos e permitir novo login
        if (isMounted.current) {
          localStorage.removeItem("token");
          delete axios.defaults.headers.common["Authorization"];
          setUser(null);
        }
      } finally {
        if (isMounted.current) {
          setLoading(false);
        }
      }
    };
  
    const login = async (email, senha) => {
      const response = await axios.post(`${API}/auth/login`, { email, senha });
      const { access_token, user: userData } = response.data;
  
      localStorage.setItem("token", access_token);
      axios.defaults.headers.common["Authorization"] = `Bearer ${access_token}`;
      setToken(access_token);
      setUser(userData);
  
      return userData;
    };
  
    const logout = () => {
      localStorage.removeItem("token");
      delete axios.defaults.headers.common["Authorization"];
      setToken(null);
      setUser(null);
    };
  
    return (
      <AuthContext.Provider value={{ user, setUser, login, logout, loading }}>
        {children}
      </AuthContext.Provider>
    );
  };
  
  // 🚀 HOOK: Chamadas Pendentes (Sistema de Attendance)
  const usePendingAttendances = () => {
    const { user } = useAuth();
    const [pending, setPending] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
  
    const fetchPending = async () => {
      if (user?.tipo !== "instrutor") {
        setPending([]);
        setLoading(false);
        return;
      }
  
      try {
        setLoading(true);
        const response = await axios.get(
          `${API}/instructor/me/pending-attendances`,
        );
        setPending(response.data.pending || []);
        setError(null);
      } catch (err) {
        console.error("Erro ao buscar chamadas pendentes:", err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
  
    useEffect(() => {
      fetchPending();
    }, [user]);
  
    // Remover turma da lista após chamada feita
    const markAttendanceComplete = (turmaId) => {
      setPending((prev) => prev.filter((p) => p.turma_id !== turmaId));
    };
  
    return {
      pending,
      loading,
      error,
      refetch: fetchPending,
      markComplete: markAttendanceComplete,
    };
  };
  
  // 🚀 COMPONENTE: Modal de Chamada
  const AttendanceModal = ({ open, onClose, turma, onComplete }) => {
    const { toast } = useToast();
    const [saving, setSaving] = useState(false);
    const [observacao, setObservacao] = useState("");
    const [showConfirm, setShowConfirm] = useState(false);
  
    // Inicializar todos os alunos como presentes
    const [records, setRecords] = useState(
      turma?.alunos?.map((aluno) => ({
        aluno_id: aluno.id,nome: aluno.nome_social || aluno.nome || `CPF: ${aluno.cpf}` || "Aluno sem nome",presente: true,
      })) || [],
    );
  
    // Atualizar records quando turma mudar
    useEffect(() => {
      if (turma?.alunos) {
        setRecords(
          turma.alunos.map((aluno) => ({
            aluno_id: aluno.id,
            nome: aluno.nome_social || aluno.nome || `CPF: ${aluno.cpf}` || "Aluno sem nome",
            presente: true,
          })),
        );
      }
    }, [turma]);
  
    const togglePresence = (index) => {
      const newRecords = [...records];
      newRecords[index].presente = !newRecords[index].presente;
      setRecords(newRecords);
    };
  
    const handleSave = async () => {
      if (!showConfirm) {
        setShowConfirm(true);
        return;
      }
  
      setSaving(true);
      try {
        // Preparar dados para envio
        const recordsToSend = records.map((r) => ({
          aluno_id: r.aluno_id,
          presente: r.presente,
          nota: r.nota || "",
        }));
  
        // Usar endpoint com data específica para permitir chamadas retroativas
        const dataUrl =
          turma.data_pendente || new Date().toISOString().split("T")[0];
        await axios.post(
          `${API}/classes/${turma.turma_id}/attendance/${dataUrl}`,
          {
            records: recordsToSend,
            observacao,
          },
        );
  
        toast({
          title: "✅ Chamada Salva",
          description: `Chamada de ${turma.turma_nome} registrada com sucesso`,
        });
  
        // 🎯 FECHAR MODAL E ATUALIZAR LISTA
        onComplete(); // Notificar componente pai para remover da lista
        onClose(); // Fechar o modal
      } catch (error) {
        if (error.response?.status === 409) {
          toast({
            title: "⚠️ Chamada Já Realizada",
            description: "A chamada desta turma já foi registrada hoje",
            variant: "destructive",
          });
        } else {
          toast({
            title: "❌ Erro",
            description: "Erro ao salvar chamada. Tente novamente.",
            variant: "destructive",
          });
        }
      } finally {
        setSaving(false);
        setShowConfirm(false);
      }
    };
  
    const presenteCount = records.filter((r) => r.presente).length;
    const absentCount = records.length - presenteCount;
  
    return (
      <Dialog open={open} onOpenChange={onClose}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>
              📋 Chamada: {turma?.turma_nome}
              {turma?.data_pendente && (
                <span className="text-sm font-normal text-gray-600 ml-2">
                  (
                  {new Date(turma.data_pendente + "T00:00:00").toLocaleDateString(
                    "pt-BR",
                  )}
                  )
                </span>
              )}
            </DialogTitle>
            <DialogDescription>
              {turma?.status_msg || "Marque os alunos presentes."} A chamada será
              salva e não poderá ser alterada.
            </DialogDescription>
          </DialogHeader>
  
          <div className="space-y-4">
            {/* Resumo */}
            <div className="flex gap-4 p-3 bg-gray-50 rounded-lg">
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {presenteCount}
                </div>
                <div className="text-sm text-green-700">Presentes</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-red-600">
                  {absentCount}
                </div>
                <div className="text-sm text-red-700">Ausentes</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {records.length}
                </div>
                <div className="text-sm text-blue-700">Total</div>
              </div>
            </div>
  
            {/* Lista de Alunos */}
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {Array.isArray(records) &&
                records.map((record, index) => (
                  <div
                    key={record.aluno_id}
                    className={`flex items-center justify-between p-3 rounded-lg border ${
                      record.presente
                        ? "bg-green-50 border-green-200"
                        : "bg-red-50 border-red-200"
                    }`}
                  >
                    <span className="font-medium">{record.nome}</span><div className="flex flex-col gap-1 items-end">
                    <div className="flex items-center space-x-2">
                      <Checkbox
                        checked={record.presente}
                        onCheckedChange={() => togglePresence(index)}
                      />
                      <span className={`text-sm font-medium ${record.presente ? "text-green-700" : "text-red-700"}`}>
                        {record.presente ? "Presente" : "Ausente"}
                      </span>
                    </div>
                    {!record.presente && (
                      <input
                        type="text"
                        placeholder="Observação (opcional)"
                        value={record.nota || ""}
                        onChange={(e) => {
                          const newRecords = [...records];
                          newRecords[index].nota = e.target.value;
                          setRecords(newRecords);
                        }}
                        className="text-xs border rounded px-2 py-1 w-48 text-gray-600"
                      />
                    )}
                  </div>
  
            {/* Observações */}
            <div className="space-y-2">
              <Label>Observações da Aula (opcional)</Label>
              <Textarea
                value={observacao}
                onChange={(e) => setObservacao(e.target.value)}
                placeholder="Anote observações sobre a aula, conteúdo ministrado, etc..."
                rows={3}
              />
            </div>
  
            {/* Confirmação */}
            {showConfirm && (
              <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <p className="text-yellow-800 font-medium">
                  ⚠️ Confirmação Necessária
                </p>
                <p className="text-yellow-700 text-sm mt-1">
                  A chamada será salva e <strong>não poderá ser alterada</strong>.
                  Deseja continuar?
                </p>
              </div>
            )}
  
            {/* Botões */}
            <div className="flex justify-end space-x-2 pt-4">
              <Button variant="outline" onClick={onClose} disabled={saving}>
                Cancelar
              </Button>
              <Button
                onClick={handleSave}
                disabled={saving}
                className={
                  showConfirm
                    ? "bg-red-600 hover:bg-red-700"
                    : "bg-blue-600 hover:bg-blue-700"
                }
              >
                {saving ? (
                  <span className="flex items-center gap-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    Salvando...
                  </span>
                ) : showConfirm ? (
                  "✅ Confirmar e Salvar"
                ) : (
                  "💾 Salvar Chamada"
                )}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    );
  };
  
  // 🚀 COMPONENTE: Card de Chamada Pendente
  const PendingAttendanceCard = ({ turma, onComplete }) => {
    const [modalOpen, setModalOpen] = useState(false);
  
    const handleComplete = () => {
      setModalOpen(false);
      onComplete(turma.turma_id);
    };
  
    // Definir cores baseadas na prioridade
    const getPriorityStyle = (prioridade) => {
      switch (prioridade) {
        case "urgente":
          return {
            cardClass: "border-red-300 bg-red-50",
            badgeClass: "text-red-700 border-red-400 bg-red-100",
            textClass: "text-red-800",
            buttonClass: "bg-red-600 hover:bg-red-700",
          };
        case "importante":
          return {
            cardClass: "border-orange-300 bg-orange-50",
            badgeClass: "text-orange-700 border-orange-400 bg-orange-100",
            textClass: "text-orange-800",
            buttonClass: "bg-orange-600 hover:bg-orange-700",
          };
        default:
          return {
            cardClass: "border-yellow-300 bg-yellow-50",
            badgeClass: "text-yellow-700 border-yellow-400 bg-yellow-100",
            textClass: "text-yellow-800",
            buttonClass: "bg-yellow-600 hover:bg-yellow-700",
          };
      }
    };
  
    const styles = getPriorityStyle(turma.prioridade);
  
    // Formatar data brasileira
    const formatDate = (dateStr) => {
      try {
        const date = new Date(dateStr + "T00:00:00");
        return date.toLocaleDateString("pt-BR");
      } catch {
        return dateStr;
      }
    };
  
    return (
      <>
        <Card className={styles.cardClass}>
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className={`text-lg ${styles.textClass}`}>
                {turma.turma_nome}
              </CardTitle>
              <Badge variant="outline" className={styles.badgeClass}>
                {turma.prioridade?.charAt(0).toUpperCase() +
                  turma.prioridade?.slice(1)}
              </Badge>
            </div>
            {/* Status da chamada */}
            <div className={`text-sm ${styles.textClass} opacity-90`}>
              {turma.status_msg}
            </div>
          </CardHeader>
  
          <CardContent className="space-y-3">
            <div
              className={`flex items-center gap-4 text-sm ${styles.textClass} opacity-80`}
            >
              <div className="flex items-center gap-1">
                <Clock className="h-4 w-4" />
                <span>{turma.horario || "Horário não definido"}</span>
              </div>
              <div className="flex items-center gap-1">
                <Users className="h-4 w-4" />
                <span>{turma.alunos?.length || 0} alunos</span>
              </div>
              <div className="flex items-center gap-1">
                <Calendar className="h-4 w-4" />
                <span>{formatDate(turma.data_pendente)}</span>
              </div>
            </div>
  
            <Button
              onClick={() => setModalOpen(true)}
              className={`w-full text-white ${styles.buttonClass}`}
            >
              📋 Fazer Chamada
            </Button>
          </CardContent>
        </Card>
  
        <AttendanceModal
          open={modalOpen}
          onClose={() => setModalOpen(false)}
          turma={turma}
          onComplete={handleComplete}
        />
      </>
    );
  };

// ============================================================
// 📝 MODAL: Professor solicita correção de chamada
// ============================================================
const AttendanceChangeRequestModal = ({ open, onClose }) => {
  const { user } = useAuth();
  const { toast } = useToast();
  const [turmas, setTurmas] = useState([]);
  const [alunos, setAlunos] = useState([]);
  const [saving, setSaving] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [form, setForm] = useState({
    turma_id: "",
    aluno_id: "",
    aluno_cpf: "",
    data_chamada: "",
    status_solicitado: "",
    motivo: "",
    tipo: "alteracao_presenca",
  });

  useEffect(() => {
    if (open) fetchTurmas();
  }, [open]);

  const fetchTurmas = async () => {
    try {
      const res = await axios.get(`${API}/classes`);
      setTurmas(Array.isArray(res.data) ? res.data : []);
    } catch {
      setTurmas([]);
    }
  };

  const fetchAlunos = async (turmaId) => {
    try {
      const res = await axios.get(`${API}/classes/${turmaId}/students`);
      setAlunos(Array.isArray(res.data) ? res.data : []);
    } catch {
      setAlunos([]);
    }
  };

  const handleTurmaChange = (turmaId) => {
    setForm((f) => ({ ...f, turma_id: turmaId, aluno_id: "", aluno_cpf: "" }));
    fetchAlunos(turmaId);
  };

  const handleAlunoChange = (alunoId) => {
    const aluno = alunos.find((a) => a.id === alunoId);
    setForm((f) => ({ ...f, aluno_id: alunoId, aluno_cpf: aluno?.cpf || "" }));
  };

  const handleSubmit = async () => {
    if (
  !form.turma_id ||
  !form.aluno_id ||
  !form.data_chamada ||
  (form.tipo === "alteracao_presenca" && form.status_solicitado === "") ||
  !form.motivo.trim()
) {
      toast({
        title: "Preencha todos os campos obrigatórios",
        variant: "destructive",
      });
      return;
    }

    setSaving(true);
    try {
      const fd = new FormData();
      fd.append("turma_id", form.turma_id);
      fd.append("aluno_id", form.aluno_id);
      fd.append("aluno_cpf", form.aluno_cpf);
      fd.append("data_chamada", form.data_chamada);
      fd.append("status_solicitado", form.tipo === "justificativa_posterior" ? "" : form.status_solicitado);
      fd.append("motivo", form.motivo);
      fd.append("tipo", form.tipo);
      if (selectedFile) fd.append("file", selectedFile);

      await axios.post(`${API}/attendance-change-requests`, fd, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      toast({
        title: "✅ Solicitação enviada!",
        description: "O administrador será notificado para revisar.",
      });

      setForm({
        turma_id: "",
        aluno_id: "",
        aluno_cpf: "",
        data_chamada: "",
        status_solicitado: "",
        motivo: "",
        tipo: "alteracao_presenca",
      });
      setSelectedFile(null);
      onClose();
      } catch (err) {
            const detail = err.response?.data?.detail;
            toast({
              title: "Erro ao enviar solicitação",
              description: typeof detail === "string"
                ? detail
                : Array.isArray(detail)
                ? detail.map(d => d.msg || JSON.stringify(d)).join(", ")
                : "Tente novamente",
              variant: "destructive",
            });
          }
    finally {
      setSaving(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-lg max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>📝 Solicitar Correção de Chamada</DialogTitle>
          <DialogDescription>
            Preencha os dados abaixo. O administrador irá revisar e aprovar ou
            negar a alteração.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* Tipo de solicitação */}
          <div className="space-y-2">
            <Label>Tipo de Solicitação *</Label>
            <Select
              value={form.tipo}
              onValueChange={(v) => setForm((f) => ({ ...f, tipo: v }))}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="alteracao_presenca">
                  Corrigir presença ou falta marcada errada
                </SelectItem>
                <SelectItem value="justificativa_posterior">
                  Adicionar justificativa com documento depois da chamada
                </SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Turma */}
          <div className="space-y-2">
            <Label>Turma *</Label>
            <Select value={form.turma_id} onValueChange={handleTurmaChange}>
              <SelectTrigger>
                <SelectValue placeholder="Selecione a turma" />
              </SelectTrigger>
              <SelectContent>
                {turmas.map((t) => (
                  <SelectItem key={t.id} value={t.id}>
                    {t.nome}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Aluno */}
          <div className="space-y-2">
            <Label>Aluno *</Label>
            <Select
              value={form.aluno_id}
              onValueChange={handleAlunoChange}
              disabled={!form.turma_id}
            >
              <SelectTrigger>
                <SelectValue
                  placeholder={
                    form.turma_id
                      ? "Selecione o aluno"
                      : "Selecione a turma primeiro"
                  }
                />
              </SelectTrigger>
              <SelectContent>
                {alunos.map((a) => (
                  <SelectItem key={a.id} value={a.id}>
                    {a.nome_social || a.nome}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Data da chamada */}
          <div className="space-y-2">
            <Label>Data da Chamada que deseja corrigir *</Label>
            <Input
              type="date"
              value={form.data_chamada}
              max={new Date().toISOString().split("T")[0]}
              onChange={(e) =>
                setForm((f) => ({ ...f, data_chamada: e.target.value }))
              }
            />
          </div>

          {/* Alterar para (apenas para alteração de presença) */}
          {form.tipo === "alteracao_presenca" && (
            <div className="space-y-2">
              <Label>Alterar o status do aluno para *</Label>
              <Select
                value={String(form.status_solicitado)}
                onValueChange={(v) =>
                  setForm((f) => ({ ...f, status_solicitado: v }))
                }
              >
                <SelectTrigger>
                  <SelectValue placeholder="Selecione o status correto" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="true">✅ Presente</SelectItem>
                  <SelectItem value="false">❌ Ausente</SelectItem>
                </SelectContent>
              </Select>
            </div>
          )}

          {/* Motivo */}
          <div className="space-y-2">
            <Label>Motivo da solicitação *</Label>
            <Textarea
              value={form.motivo}
              onChange={(e) =>
                setForm((f) => ({ ...f, motivo: e.target.value }))
              }
              placeholder="Explique por que precisa corrigir esta chamada. Ex: Marquei falta sem querer, aluno estava presente."
              rows={3}
            />
          </div>

          {/* Documento */}
          <div className="space-y-2">
            <Label>Documento comprobatório (opcional)</Label>
            <Input
              type="file"
              accept=".pdf,.jpg,.jpeg,.png"
              onChange={(e) => setSelectedFile(e.target.files[0])}
            />
            <p className="text-xs text-gray-500">
              Atestado, declaração ou outro documento — PDF, JPG, PNG (máx. 5MB)
            </p>
          </div>

          {/* Aviso */}
          <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
            <p className="text-sm text-yellow-800">
              ⚠️ A solicitação será enviada ao administrador. Somente após
              aprovação a chamada será alterada.
            </p>
          </div>

          {/* Botões */}
          <div className="flex justify-end space-x-2 pt-2">
            <Button variant="outline" onClick={onClose} disabled={saving}>
              Cancelar
            </Button>
            <Button
              onClick={handleSubmit}
              disabled={saving}
              className="bg-blue-600 hover:bg-blue-700"
            >
              {saving ? (
                <span className="flex items-center gap-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  Enviando...
                </span>
              ) : (
                "📤 Enviar Solicitação"
              )}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};
// ============================================================
// 🛡️ PAINEL ADMIN: Ver e responder solicitações de correção
// ============================================================
  const AdminReactivationPanel = () => {
  const { toast } = useToast();
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [respondingId, setRespondingId] = useState(null);
  const [resposta, setResposta] = useState("");

  useEffect(() => { fetchRequests(); }, []);

  const fetchRequests = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API}/reactivation-requests?status=pendente`);
      setRequests(Array.isArray(res.data) ? res.data : []);
    } catch {
      setRequests([]);
    } finally {
      setLoading(false);
    }
  };

  const handleRespond = async (id, decision) => {
    try {
      await axios.put(
        `${API}/reactivation-requests/${id}/respond?decision=${decision}${resposta ? `&resposta=${encodeURIComponent(resposta)}` : ""}`
      );
      toast({
        title: decision === "aprovado" ? "✅ Aluno reativado!" : "❌ Solicitação negada",
      });
      setRespondingId(null);
      setResposta("");
      fetchRequests();
    } catch (err) {
      toast({ title: "Erro ao responder", variant: "destructive" });
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <RefreshCw className="h-5 w-5 text-green-600" />
          Solicitações de Reativação de Alunos
        </CardTitle>
        <CardDescription>Alunos desistentes que solicitaram retorno ao curso</CardDescription>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="text-center py-8"><RefreshCw className="h-6 w-6 animate-spin mx-auto text-gray-400" /></div>
        ) : requests.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <CheckCircle className="h-10 w-10 mx-auto mb-3 text-green-400" />
            <p>Nenhuma solicitação pendente.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {requests.map((req) => (
              <Card key={req.id} className="border-l-4 border-l-green-500">
                <CardContent className="p-4">
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <p className="font-semibold text-gray-900">{req.aluno_nome}</p>
                      <p className="text-sm text-gray-600">Solicitado por: {req.solicitado_por_nome}</p>
                    </div>
                    <Badge variant="outline">⏳ Pendente</Badge>
                  </div>
                  {req.motivo && (
                    <div className="p-2 bg-blue-50 border border-blue-100 rounded-lg mb-3">
                      <p className="text-sm text-blue-700"><strong>Motivo:</strong> {req.motivo}</p>
                    </div>
                  )}
                  <div className="mt-3 pt-3 border-t">
                    {respondingId === req.id ? (
                      <div className="space-y-3">
                        <Textarea
                          value={resposta}
                          onChange={(e) => setResposta(e.target.value)}
                          placeholder="Observação para o professor (opcional)..."
                          rows={2}
                        />
                        <div className="flex gap-2">
                          <Button size="sm" onClick={() => handleRespond(req.id, "aprovado")} className="bg-green-600 hover:bg-green-700">
                            <CheckCircle className="h-4 w-4 mr-1" /> Aprovar Reativação
                          </Button>
                          <Button size="sm" onClick={() => handleRespond(req.id, "negado")} className="bg-red-600 hover:bg-red-700">
                            <X className="h-4 w-4 mr-1" /> Negar
                          </Button>
                          <Button size="sm" variant="outline" onClick={() => { setRespondingId(null); setResposta(""); }}>
                            Cancelar
                          </Button>
                        </div>
                      </div>
                    ) : (
                      <Button size="sm" variant="outline" onClick={() => setRespondingId(req.id)} className="border-green-400 text-green-600 hover:bg-green-50">
                        <Edit className="h-4 w-4 mr-1" /> Responder
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
        <div className="mt-4 flex justify-end">
          <Button variant="outline" size="sm" onClick={fetchRequests}>
            <RefreshCw className="h-4 w-4 mr-1" /> Atualizar
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};
const AdminChangeRequestsPanel = () => {
  const { toast } = useToast();
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [respondingId, setRespondingId] = useState(null);
  const [resposta, setResposta] = useState("");
  const [filterStatus, setFilterStatus] = useState("pendente");

  useEffect(() => {
    fetchRequests();
  }, [filterStatus]);

  const fetchRequests = async () => {
    setLoading(true);
    try {
      const url = filterStatus
        ? `${API}/attendance-change-requests?status=${filterStatus}`
        : `${API}/attendance-change-requests`;
      const res = await axios.get(url);
      setRequests(Array.isArray(res.data) ? res.data : []);
    } catch (err) {
      console.error("Erro ao buscar solicitações:", err?.response?.data || err);      
      setRequests([]);
    } finally {
      setLoading(false);
    }
  };

  const handleRespond = async (id, decision) => {
    try {
      await axios.put(
        `${API}/attendance-change-requests/${id}/respond?decision=${decision}&resposta=${encodeURIComponent(resposta)}`
      );
      toast({
        title:
          decision === "aprovado"
            ? "✅ Solicitação aprovada e chamada corrigida!"
            : "❌ Solicitação negada",
        description:
          decision === "aprovado"
            ? "A chamada foi alterada automaticamente no sistema."
            : "O professor foi notificado da negação.",
      });
      setRespondingId(null);
      setResposta("");
      fetchRequests();
    } catch (err) {
      toast({
        title: "Erro ao responder",
        description: typeof err.response?.data?.detail === "string"
        ? err.response.data.detail
        : "Tente novamente",
        variant: "destructive",
      });
    }
  };

  const statusLabel = {
    pendente: "⏳ Pendentes",
    aprovado: "✅ Aprovadas",
    negado: "❌ Negadas",
  };

  const statusBorderColor = {
    pendente: "border-l-yellow-500",
    aprovado: "border-l-green-500",
    negado: "border-l-red-500",
  };

  const formatDate = (dateStr) => {
    try {
      return new Date(dateStr + "T00:00:00").toLocaleDateString("pt-BR");
    } catch {
      return dateStr;
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileText className="h-5 w-5 text-blue-600" />
          Solicitações de Correção de Chamada
        </CardTitle>
        <CardDescription>
          Revise e aprove ou negue as solicitações enviadas pelos professores
        </CardDescription>
      </CardHeader>
      <CardContent>
        {/* Filtros de status */}
        <div className="flex gap-2 mb-6">
          {["pendente", "aprovado", "negado"].map((s) => (
            <Button
              key={s}
              variant={filterStatus === s ? "default" : "outline"}
              size="sm"
              onClick={() => setFilterStatus(s)}
            >
              {statusLabel[s]}
            </Button>
          ))}
        </div>

        {loading ? (
          <div className="text-center py-8">
            <RefreshCw className="h-6 w-6 animate-spin mx-auto text-gray-400 mb-2" />
            <p className="text-gray-500">Carregando solicitações...</p>
          </div>
        ) : requests.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <CheckCircle className="h-10 w-10 mx-auto mb-3 text-green-400" />
            <p>Nenhuma solicitação {filterStatus} no momento.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {requests.map((req) => (
              <Card
                key={req.id}
                className={`border-l-4 ${
                  statusBorderColor[req.status_solicitacao] ||
                  "border-l-gray-300"
                }`}
              >
                <CardContent className="p-4">
                  {/* Cabeçalho do card */}
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <p className="font-semibold text-gray-900 text-base">
                        {req.aluno_nome}
                        <span className="text-sm text-gray-500 font-normal ml-2">
                          CPF: {req.aluno_cpf}
                        </span>
                      </p>
                      <p className="text-sm text-gray-600 mt-1">
                        <strong>Turma:</strong> {req.turma_nome} |{" "}
                        <strong>Data da chamada:</strong>{" "}
                        {formatDate(req.data_chamada)}
                      </p>
                      <p className="text-sm text-gray-600">
                        <strong>Solicitado por:</strong> {req.solicitado_por_nome}
                      </p>
                    </div>
                    <Badge
                      variant={
                        req.status_solicitacao === "aprovado"
                          ? "default"
                          : req.status_solicitacao === "negado"
                          ? "destructive"
                          : "outline"
                      }
                    >
                      {req.status_solicitacao === "pendente"
                        ? "⏳ Pendente"
                        : req.status_solicitacao === "aprovado"
                        ? "✅ Aprovado"
                        : "❌ Negado"}
                    </Badge>
                  </div>

                  {/* Tipo e alteração */}
                  <div className="p-2 bg-gray-50 rounded-lg mb-3 text-sm">
                    <p>
                      <strong>Tipo:</strong>{" "}
                      {req.tipo === "alteracao_presenca"
                        ? "Correção de presença/falta"
                        : "Justificativa posterior"}
                    </p>
                    {req.tipo === "alteracao_presenca" && (
                      <p>
                        <strong>Alteração pedida:</strong>{" "}
                        {req.status_atual ? "✅ Presente" : "❌ Ausente"} →{" "}
                        {req.status_solicitado ? "✅ Presente" : "❌ Ausente"}
                      </p>
                    )}
                  </div>

                  {/* Motivo */}
                  <div className="p-2 bg-blue-50 border border-blue-100 rounded-lg mb-3">
                    <p className="text-sm font-medium text-blue-800 mb-1">
                      Motivo informado:
                    </p>
                    <p className="text-sm text-blue-700">{req.motivo}</p>
                  </div>

                  {/* Documento anexado */}
                  {req.arquivo_nome && (
                    <p className="text-xs text-gray-500 mb-3">
                      📎 Documento anexado: {req.arquivo_nome}
                    </p>
                  )}

                  {/* Resposta do admin (se já respondido) */}
                  {req.admin_resposta && (
                    <div className="p-2 bg-gray-100 rounded-lg mb-3">
                      <p className="text-xs text-gray-500">
                        Resposta do admin ({req.respondido_por_nome}):{" "}
                        {req.admin_resposta}
                      </p>
                    </div>
                  )}

                  {/* Área de resposta (apenas se pendente) */}
                  {req.status_solicitacao === "pendente" && (
                    <div className="mt-3 pt-3 border-t">
                      {respondingId === req.id ? (
                        <div className="space-y-3">
                          <Textarea
                            value={resposta}
                            onChange={(e) => setResposta(e.target.value)}
                            placeholder="Adicione uma observação para o professor (opcional)..."
                            rows={2}
                            className="text-sm"
                          />
                          <div className="flex gap-2">
                            <Button
                              size="sm"
                              onClick={() => handleRespond(req.id, "aprovado")}
                              className="bg-green-600 hover:bg-green-700"
                            >
                              <CheckCircle className="h-4 w-4 mr-1" />
                              Aprovar e Corrigir Chamada
                            </Button>
                            <Button
                              size="sm"
                              onClick={() => handleRespond(req.id, "negado")}
                              className="bg-red-600 hover:bg-red-700"
                            >
                              <X className="h-4 w-4 mr-1" />
                              Negar
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => {
                                setRespondingId(null);
                                setResposta("");
                              }}
                            >
                              Cancelar
                            </Button>
                          </div>
                        </div>
                      ) : (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => setRespondingId(req.id)}
                          className="border-blue-400 text-blue-600 hover:bg-blue-50"
                        >
                          <Edit className="h-4 w-4 mr-1" />
                          Responder esta solicitação
                        </Button>
                      )}
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        <div className="mt-4 flex justify-end">
          <Button variant="outline" size="sm" onClick={fetchRequests}>
            <RefreshCw className="h-4 w-4 mr-1" />
            Atualizar lista
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

// ============================================================
// 🔐 PÁGINA OBRIGATÓRIA DE TROCA DE SENHA (PRIMEIRO ACESSO)
// ============================================================
const PrimeiroAcessoPage = ({ onSenhaAlterada }) => {
  const { user } = useAuth();
  const { toast } = useToast();
  const [senhaAtual, setSenhaAtual] = useState("");
  const [novaSenha, setNovaSenha] = useState("");
  const [confirmarSenha, setConfirmarSenha] = useState("");
  const [salvando, setSalvando] = useState(false);
  const [mostrarSenhas, setMostrarSenhas] = useState(false);

  const handleTrocarSenha = async () => {
    if (!senhaAtual || !novaSenha || !confirmarSenha) {
      toast({
        title: "Preencha todos os campos",
        variant: "destructive",
      });
      return;
    }

    if (novaSenha.length < 6) {
      toast({
        title: "Senha muito curta",
        description: "A nova senha deve ter pelo menos 6 caracteres.",
        variant: "destructive",
      });
      return;
    }

    if (novaSenha !== confirmarSenha) {
      toast({
        title: "As senhas não coincidem",
        description: "A nova senha e a confirmação precisam ser iguais.",
        variant: "destructive",
      });
      return;
    }

    if (novaSenha === senhaAtual) {
      toast({
        title: "Senha igual à atual",
        description: "A nova senha deve ser diferente da senha temporária.",
        variant: "destructive",
      });
      return;
    }

    setSalvando(true);
    try {
      await axios.post(
        `${API}/auth/change-password`,
        { senha_atual: senhaAtual, nova_senha: novaSenha },
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        }
      );

      toast({
        title: "✅ Senha alterada com sucesso!",
        description: "Bem-vindo ao sistema. Você será redirecionado agora.",
      });

      // Aguarda 1 segundo para o usuário ver o toast e depois libera o sistema
      setTimeout(() => {
        onSenhaAlterada();
      }, 1500);
    } catch (err) {
      toast({
        title: "Erro ao trocar senha",
        description:
          err.response?.data?.detail ||
          "Verifique se a senha atual está correta.",
        variant: "destructive",
      });
    } finally {
      setSalvando(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Card principal */}
        <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-600 to-indigo-600 p-6 text-white text-center">
            <div className="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center mx-auto mb-3">
              <Lock className="h-8 w-8 text-white" />
            </div>
            <h1 className="text-2xl font-bold">Primeiro Acesso</h1>
            <p className="text-blue-100 text-sm mt-1">
              Olá, {user?.nome?.split(" ")[0]}! Troque sua senha para continuar.
            </p>
          </div>

          {/* Aviso */}
          <div className="mx-6 mt-5 p-3 bg-yellow-50 border border-yellow-200 rounded-lg flex gap-2">
            <AlertTriangle className="h-5 w-5 text-yellow-600 flex-shrink-0 mt-0.5" />
            <p className="text-sm text-yellow-800">
              Por segurança, você precisa trocar a senha temporária antes de
              usar o sistema.
            </p>
          </div>

          {/* Formulário */}
          <div className="p-6 space-y-4">
            <div className="space-y-2">
              <Label className="text-gray-700 font-medium">
                Senha temporária atual
              </Label>
              <div className="relative">
                <Input
                  type={mostrarSenhas ? "text" : "password"}
                  value={senhaAtual}
                  onChange={(e) => setSenhaAtual(e.target.value)}
                  placeholder="Digite sua senha temporária"
                  className="pr-10"
                />
                <button
                  type="button"
                  onClick={() => setMostrarSenhas(!mostrarSenhas)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  {mostrarSenhas ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </button>
              </div>
            </div>

            <div className="space-y-2">
              <Label className="text-gray-700 font-medium">Nova senha</Label>
              <Input
                type={mostrarSenhas ? "text" : "password"}
                value={novaSenha}
                onChange={(e) => setNovaSenha(e.target.value)}
                placeholder="Mínimo 6 caracteres"
              />
            </div>

            <div className="space-y-2">
              <Label className="text-gray-700 font-medium">
                Confirmar nova senha
              </Label>
              <Input
                type={mostrarSenhas ? "text" : "password"}
                value={confirmarSenha}
                onChange={(e) => setConfirmarSenha(e.target.value)}
                placeholder="Repita a nova senha"
                onKeyDown={(e) => e.key === "Enter" && handleTrocarSenha()}
              />
            </div>

            {/* Indicador de força da senha */}
            {novaSenha && (
              <div className="space-y-1">
                <div className="flex gap-1">
                  {[1, 2, 3, 4].map((nivel) => (
                    <div
                      key={nivel}
                      className={`h-1.5 flex-1 rounded-full transition-colors ${
                        novaSenha.length >= nivel * 3
                          ? nivel <= 1
                            ? "bg-red-400"
                            : nivel <= 2
                            ? "bg-yellow-400"
                            : nivel <= 3
                            ? "bg-blue-400"
                            : "bg-green-400"
                          : "bg-gray-200"
                      }`}
                    />
                  ))}
                </div>
                <p className="text-xs text-gray-500">
                  {novaSenha.length < 6
                    ? "Senha muito curta"
                    : novaSenha.length < 9
                    ? "Senha razoável"
                    : novaSenha.length < 12
                    ? "Senha boa"
                    : "Senha forte"}
                </p>
              </div>
            )}

            <Button
              onClick={handleTrocarSenha}
              disabled={salvando}
              className="w-full bg-blue-600 hover:bg-blue-700 mt-2"
            >
              {salvando ? (
                <span className="flex items-center gap-2 justify-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
                  Salvando...
                </span>
              ) : (
                <span className="flex items-center gap-2 justify-center">
                  <Lock className="h-4 w-4" />
                  Trocar Senha e Entrar no Sistema
                </span>
              )}
            </Button>
          </div>

          {/* Rodapé */}
          <div className="px-6 pb-5 text-center">
            <p className="text-xs text-gray-400">
              Senha padrão: <strong>IOS2026</strong> + suas iniciais.
              <br />
              Ex: Maria Silva Santos → <strong>IOS2026mss</strong>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
// Login Component
const Login = () => {
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [loading, setLoading] = useState(false);
  const [showFirstAccess, setShowFirstAccess] = useState(false);
  const [showResetPassword, setShowResetPassword] = useState(false);
  const [resetEmail, setResetEmail] = useState("");
  const [resetLoading, setResetLoading] = useState(false);
  const [showBrandCard, setShowBrandCard] = useState(false);
  const [firstAccessData, setFirstAccessData] = useState({
    nome: "",
    email: "",
    tipo: "instrutor",
  });
  const { login } = useAuth();
  const { toast } = useToast();
  
    // Animação do card temporal da marca
    useEffect(() => {
      // Mostrar o card após 500ms
      const showTimer = setTimeout(() => {
        setShowBrandCard(true);
      }, 500);
  
      // Esconder o card após 4 segundos
      const hideTimer = setTimeout(() => {
        setShowBrandCard(false);
      }, 4500);
  
      return () => {
        clearTimeout(showTimer);
        clearTimeout(hideTimer);
      };
    }, []);
  
    const handleSubmit = async (e) => {
      e.preventDefault();
      setLoading(true);
  
      try {
        const userData = await login(email, senha);
  
        if (userData.primeiro_acesso) {
          toast({
            title: "Primeiro acesso detectado",
            description: "Você precisa alterar sua senha",
          });
          // Redirect to change password
        } else {
          toast({
            title: "Login realizado com sucesso!",
            description: "Bem-vindo ao Sistema de Controle de Presença",
          });
        }
      } catch (error) {
        toast({
          title: "Erro no login",
          description:
            error.response?.data?.detail || "Verifique suas credenciais",
          variant: "destructive",
        });
      } finally {
        setLoading(false);
      }
    };
  
    const handleFirstAccessSubmit = async (e) => {
      e.preventDefault();
      try {
        await axios.post(`${API}/auth/first-access`, firstAccessData);
        toast({
          title: "Solicitação enviada!",
          description:
            "Aguarde a aprovação do administrador para acessar o sistema.",
        });
        setShowFirstAccess(false);
        setFirstAccessData({ nome: "", email: "", tipo: "instrutor" });
      } catch (error) {
        toast({
          title: "Erro na solicitação",
          description: error.response?.data?.detail || "Tente novamente",
          variant: "destructive",
        });
      }
    };
  
    const handleResetPasswordSubmit = async (e) => {
      e.preventDefault();
      setResetLoading(true);
  
      try {
        const response = await axios.post(`${API}/auth/reset-password-request`, {
          email: resetEmail,
        });
  
        // 🔐 SEGURANÇA: Não mostra mais a senha na tela
        toast({
          title: "Solicitação enviada!",
          description: response.data.message,
          variant: "default",
        });
        setShowResetPassword(false);
        setResetEmail("");
      } catch (error) {
        toast({
          title: "Erro ao resetar senha",
          description: error.response?.data?.detail || "Tente novamente",
          variant: "destructive",
        });
      } finally {
        setResetLoading(false);
      }
    };
  
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-orange-50 flex items-center justify-center p-4 relative">
        <Card className="w-full max-w-md shadow-xl border-purple-200">
          <CardHeader className="text-center">
            {/* Logo principal do sistema + nome */}
            <div className="login-header mb-6">
              <img
                src="/logo-sistema.jpg"
                alt="Logo do Sistema IOS"
                className="system-logo h-32 w-auto object-contain mx-auto mb-4 opacity-95 transition-all duration-700 ease-in-out animate-fade-in"
              />
              <h1 className="system-name text-3xl font-semibold text-center tracking-wide font-poppins bg-gradient-to-r from-purple-600 to-orange-500 bg-clip-text text-transparent">
                IOS
              </h1>
            </div>
            <CardDescription className="text-gray-600">
              Sistema de Controle de Presença
            </CardDescription>
          </CardHeader>
          <CardContent>
            {!showFirstAccess && !showResetPassword ? (
              <>
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="email">Email</Label>
                    <Input
                      id="email"
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="admin@ios.com.br"
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="senha">Senha</Label>
                    <Input
                      id="senha"
                      type="password"
                      value={senha}
                      onChange={(e) => setSenha(e.target.value)}
                      placeholder="Digite sua senha"
                      required
                    />
                  </div>
                  <Button
                    type="submit"
                    className="w-full bg-gradient-to-r from-purple-600 to-orange-500 hover:from-purple-700 hover:to-orange-600 text-white shadow-lg"
                    disabled={loading}
                  >
                    {loading ? "Entrando..." : "Entrar"}
                  </Button>
                </form>
              </>
            ) : showResetPassword ? (
              <form onSubmit={handleResetPasswordSubmit} className="space-y-4">
                <div className="text-center mb-4">
                  <h3 className="text-lg font-semibold">Resetar Senha</h3>
                  <p className="text-sm text-gray-600">
                    Digite seu email para receber uma nova senha temporária
                  </p>
                </div>
  
                <div className="space-y-2">
                  <Label htmlFor="reset-email">Email</Label>
                  <Input
                    id="reset-email"
                    type="email"
                    value={resetEmail}
                    onChange={(e) => setResetEmail(e.target.value)}
                    placeholder="seu@email.com"
                    required
                  />
                </div>
  
                <div className="flex space-x-2">
                  <Button
                    type="button"
                    variant="outline"
                    className="flex-1 border-purple-300 text-purple-600 hover:bg-purple-50"
                    onClick={() => setShowResetPassword(false)}
                  >
                    Voltar
                  </Button>
                  <Button
                    type="submit"
                    className="flex-1 bg-gradient-to-r from-purple-600 to-orange-500 hover:from-purple-700 hover:to-orange-600 text-white"
                    disabled={resetLoading}
                  >
                    {resetLoading ? "Resetando..." : "Resetar Senha"}
                  </Button>
                </div>
              </form>
            ) : (
              <form onSubmit={handleFirstAccessSubmit} className="space-y-4">
                <div className="text-center mb-4">
                  <h3 className="text-lg font-semibold">
                    Solicitar Primeiro Acesso
                  </h3>
                  <p className="text-sm text-gray-600">
                    Preencha os dados para solicitar acesso ao sistema
                  </p>
                </div>
  
                <div className="space-y-2">
                  <Label htmlFor="nome">Nome Completo</Label>
                  <Input
                    id="nome"
                    value={firstAccessData.nome}
                    onChange={(e) =>
                      setFirstAccessData({
                        ...firstAccessData,
                        nome: e.target.value,
                      })
                    }
                    required
                  />
                </div>
  
                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    value={firstAccessData.email}
                    onChange={(e) =>
                      setFirstAccessData({
                        ...firstAccessData,
                        email: e.target.value,
                      })
                    }
                    required
                  />
                </div>
  
                <div className="space-y-2">
                  <Label>Tipo de Usuário</Label>
                  <Select
                    value={firstAccessData.tipo}
                    onValueChange={(value) =>
                      setFirstAccessData({ ...firstAccessData, tipo: value })
                    }
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="instrutor">
                        {getUserTypeLabel("instrutor")}
                      </SelectItem>
                      <SelectItem value="pedagogo">
                        {getUserTypeLabel("pedagogo")}
                      </SelectItem>
                      <SelectItem value="monitor">
                        {getUserTypeLabel("monitor")}
                      </SelectItem>
                      <SelectItem value="gestor">
                      {getUserTypeLabel("gestor")}
                      </SelectItem>
                    </SelectContent>
                  </Select>
                </div>
  
                <div className="flex space-x-2">
                  <Button
                    type="button"
                    variant="outline"
                    className="flex-1 border-purple-300 text-purple-600 hover:bg-purple-50"
                    onClick={() => setShowFirstAccess(false)}
                  >
                    Voltar
                  </Button>
                  <Button
                    type="submit"
                    className="flex-1 bg-gradient-to-r from-purple-600 to-orange-500 hover:from-purple-700 hover:to-orange-600 text-white"
                  >
                    Solicitar Acesso
                  </Button>
                </div>
              </form>
            )}
          </CardContent>
        </Card>
  
        {/* Card temporário da marca */}
        <div
          className={`fixed bottom-5 right-5 flex items-center bg-black bg-opacity-75 text-white px-4 py-2 rounded-xl shadow-lg transition-all duration-800 z-50 ${
            showBrandCard
              ? "opacity-100 transform translate-y-0"
              : "opacity-0 transform translate-y-3 pointer-events-none"
          }`}
        >
          <img
            src="/logo-amaros.svg"
            alt="Amaro's Developer Logo"
            className="h-7 mr-3"
          />
          <span className="text-sm font-normal tracking-wide">
            Sistema de Controle de Presença
          </span>
        </div>
      </div>
    );
  };
  const SolicitacaoNotifBell = () => {
  const { user } = useAuth();
  const { toast } = useToast();
  const [notifs, setNotifs] = useState([]);
  const [showDialog, setShowDialog] = useState(false);

  const fetchNotifs = async () => {
    if (!user || user.tipo === "admin") return;
    try {
      const res = await axios.get(`${API}/notifications/my?apenas_nao_lidas=true`);
      setNotifs(Array.isArray(res.data) ? res.data : []);
    } catch {
      setNotifs([]);
    }
  };

  useEffect(() => {
    fetchNotifs();
    const interval = setInterval(fetchNotifs, 2 * 60 * 1000);
    return () => clearInterval(interval);
  }, [user]);

  const marcarLida = async (id) => {
    await axios.put(`${API}/notifications/${id}/read`).catch(() => {});
    setNotifs(prev => prev.filter(n => n.id !== id));
  };

  const marcarTodasLidas = async () => {
    await axios.put(`${API}/notifications/read-all`).catch(() => {});
    setNotifs([]);
    setShowDialog(false);
  };

  if (!user || user.tipo === "admin") return null;

  return (
    <>
      <Button
        variant="ghost"
        size="sm"
        onClick={() => { setShowDialog(true); fetchNotifs(); }}
        className="relative text-gray-500 hover:text-gray-700"
        title="Notificações de solicitações"
      >
        <AlertTriangle className="h-5 w-5 text-yellow-500" />
        {notifs.length > 0 && (
          <span className="absolute -top-1 -right-1 bg-blue-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
            {notifs.length}
          </span>
        )}
      </Button>

      <Dialog open={showDialog} onOpenChange={setShowDialog}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Bell className="h-5 w-5 text-blue-600" />
              Notificações de Solicitações
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-3 max-h-80 overflow-y-auto">
            {notifs.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <CheckCircle className="h-10 w-10 mx-auto mb-2 text-green-400" />
                <p>Nenhuma notificação nova.</p>
              </div>
            ) : (
              notifs.map(n => (
                <Card key={n.id} className={`border-l-4 ${n.titulo.includes("aprovada") ? "border-l-green-500" : "border-l-red-500"}`}>
                  <CardContent className="p-3">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <p className="font-semibold text-sm">{n.titulo}</p>
                        <p className="text-xs text-gray-600 mt-1">{n.mensagem}</p>
                        <p className="text-xs text-gray-400 mt-1">
                          {new Date(n.created_at).toLocaleString("pt-BR")}
                        </p>
                      </div>
                      <Button size="sm" variant="ghost" onClick={() => marcarLida(n.id)} className="text-xs text-gray-400 hover:text-gray-600 ml-2">
                        <X className="h-3 w-3" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))
            )}
          </div>
          {notifs.length > 0 && (
            <div className="flex justify-end pt-2 border-t">
              <Button variant="outline" size="sm" onClick={marcarTodasLidas}>
                Marcar todas como lidas
              </Button>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </>
  );
};

  // 🔔 Componente de Notificações
  const NotificationButton = () => {
    const [notifications, setNotifications] = useState([]);
    const [loading, setLoading] = useState(false);
    const [showDialog, setShowDialog] = useState(false);
    const { user, setUser } = useAuth();
    const { toast } = useToast();
  
    // Buscar notificações ao montar o componente
    useEffect(() => {
      fetchNotifications();
  
      // Verificar notificações a cada 5 minutos
      const interval = setInterval(fetchNotifications, 5 * 60 * 1000);
      return () => clearInterval(interval);
    }, [user]);
  
    const fetchNotifications = async () => {
      if (!user) return;
  
      try {
        setLoading(true);
        // 🎯 USAR MESMO ENDPOINT DO SISTEMA DE CHAMADAS PENDENTES
        const response = await axios.get(
          `${API}/instructor/me/pending-attendances`,
        );
        setNotifications(response.data.pending || []);
      } catch (error) {
        console.error("Erro ao buscar notificações:", error);
      } finally {
        setLoading(false);
      }
    };
  
    const getNotificationCount = () => {
      return notifications.length;
    };
  
    const getPriorityColor = (priority) => {
      switch (priority) {
        case "alta":
          return "text-red-600";
        case "media":
          return "text-orange-600";
        default:
          return "text-yellow-600";
      }
    };
  
    const getPriorityBadge = (priority) => {
      switch (priority) {
        case "alta":
          return "bg-red-100 text-red-800";
        case "media":
          return "bg-orange-100 text-orange-800";
        default:
          return "bg-yellow-100 text-yellow-800";
      }
    };
  
    const formatDate = (dateString) => {
      const date = new Date(dateString + "T00:00:00");
      return date.toLocaleDateString("pt-BR");
    };
  
    return (
      <>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setShowDialog(true)}
          className="relative text-gray-500 hover:text-gray-700"
          title="Notificações de chamadas pendentes"
        >
          {getNotificationCount() > 0 ? (
            <BellRing className="h-5 w-5" />
          ) : (
            <Bell className="h-5 w-5" />
          )}
          {getNotificationCount() > 0 && (
            <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
              {getNotificationCount()}
            </span>
          )}
        </Button>
  
        <Dialog open={showDialog} onOpenChange={setShowDialog}>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-orange-600" />
                Chamadas Pendentes
              </DialogTitle>
              <DialogDescription>
                {getNotificationCount() === 0
                  ? "Todas as chamadas estão em dia!"
                  : `${getNotificationCount()} turma(s) sem chamada registrada`}
              </DialogDescription>
            </DialogHeader>
  
            <div className="max-h-96 overflow-y-auto">
              {loading ? (
                <div className="flex items-center justify-center py-8">
                  <RefreshCw className="h-6 w-6 animate-spin text-gray-400" />
                  <span className="ml-2 text-gray-600">Carregando...</span>
                </div>
              ) : getNotificationCount() === 0 ? (
                <div className="text-center py-8">
                  <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-4" />
                  <p className="text-gray-600">Todas as chamadas estão em dia!</p>
                  <p className="text-sm text-gray-500 mt-2">
                    Não há turmas com chamadas pendentes.
                  </p>
                </div>
                
                ) : (
                <div className="space-y-4">
                  {notifications.map((notification) => (
                    <Card key={notification.turma_id || notification.id} className="border-l-4 border-l-orange-500">
                      <CardContent className="p-4">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <h4 className="font-semibold text-gray-900 mb-2">
                              {notification.turma_nome}
                            </h4>
                            <div className="space-y-1 text-sm text-gray-600">
                              <p><strong>Horário:</strong> {notification.horario || "Não definido"}</p>
                              <p><strong>Alunos:</strong> {notification.alunos?.length || 0} alunos</p>
                            </div>
                          </div>
                          <AlertTriangle className="h-5 w-5 text-orange-600" />
                        </div>
                        <p className="text-xs text-gray-500 mt-3 italic">{notification.status_msg}</p>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </div>

            <div className="flex justify-between items-center pt-4 border-t">
              <Button
                variant="outline"
                onClick={fetchNotifications}
                disabled={loading}
                size="sm"
              >
                <RefreshCw className={`h-4 w-4 mr-2 ${loading ? "animate-spin" : ""}`} />
                Atualizar
              </Button>
              <Button onClick={() => setShowDialog(false)}>Fechar</Button>
            </div>
          </DialogContent>
        </Dialog>
      </>
    );
  };    
                      
  // Dashboard Component
  const Dashboard = () => {
    const [filtrosTurmas, setFiltrosTurmas] = useState({ nome: "", tipo: "todos", unidade: "todos", curso: "todos" });
    const [filtrosAlunos, setFiltrosAlunos] = useState({ busca: "", curso: "todos", turma: "todos" });
    const [stats, setStats] = useState({});
    const [loading, setLoading] = useState(true);
    const { user, logout } = useAuth();
    const { toast } = useToast();
  
    // 🚀 HOOK: Chamadas Pendentes
    const {
      pending,
      loading: pendingLoading,
      error: pendingError,
      refetch: refetchPending,
      markComplete,
    } = usePendingAttendances();
  
    useEffect(() => {
      fetchStats();
    }, []);
  
    const fetchStats = async () => {
      try {
        const response = await axios.get(`${API}/dashboard/stats`);
        setStats(response.data);
      } catch (error) {
        console.error("Error fetching stats:", error);
      } finally {
        setLoading(false);
      }
    };
  
    const handleLogout = () => {
      logout();
      toast({
        title: "Logout realizado",
        description: "Até logo!",
      });
    };
  
    return (
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center">
                <GraduationCap className="h-8 w-8 text-blue-600 mr-3" />
                <h1 className="text-xl font-bold text-gray-900">IOS</h1>
              </div>
              <div className="flex items-center space-x-4">
                {/* Componente de Notificações */}
                <SolicitacaoNotifBell />
                <NotificationButton />
  
                <Badge variant="outline">{getUserTypeLabel(user?.tipo)}</Badge>
                <span className="text-sm text-gray-700">{user?.nome}</span>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleLogout}
                  className="text-gray-500 hover:text-gray-700"
                  title="Sair do sistema"
                >
                  <LogOut className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>
        </header>
  
        {/* Main Content */}
        <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          {/* 📊 Dashboard Personalizado por Usuário */}
          {user?.tipo !== "admin" && (
            <div className="mb-6 p-4 bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-lg">
              <div className="flex items-center gap-3">
                <Shield className="h-6 w-6 text-blue-600" />
                <div>
                  <h3 className="font-semibold text-gray-900">
                    {stats.tipo_usuario ||
                      user?.tipo?.charAt(0).toUpperCase() + user?.tipo?.slice(1)}
                  </h3>
                  <div className="flex items-center gap-4 text-sm text-gray-600">
                    <span>
                      <Building2 className="h-4 w-4 inline mr-1" />
                      {stats.unidade_nome || "Sua unidade"}
                    </span>
                    <span>
                      <BookOpen className="h-4 w-4 inline mr-1" />
                      {stats.curso_nome || "Seu curso"}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}
  
          {/* Enhanced Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <Card className="stats-card">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">
                      {user?.tipo === "admin" ? "Unidades" : "Sua Unidade"}
                    </p>
                    <p className="text-2xl font-bold text-gray-900">
                      {stats.total_unidades || 0}
                    </p>
                  </div>
                  <Building2 className="h-8 w-8 text-blue-600" />
                </div>
              </CardContent>
            </Card>
  
            <Card className="stats-card">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">
                      {user?.tipo === "admin" ? "Cursos" : "Seu Curso"}
                    </p>
                    <p className="text-2xl font-bold text-gray-900">
                      {stats.total_cursos || 0}
                    </p>
                  </div>
                  <BookOpen className="h-8 w-8 text-green-600" />
                </div>
              </CardContent>
            </Card>
  
            <Card className="stats-card">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">
                      {user?.tipo === "admin"
                        ? "Turmas"
                        : user?.tipo === "instrutor"
                          ? "Minhas Turmas"
                          : "Turmas do Curso"}
                    </p>
                    <p className="text-2xl font-bold text-gray-900">
                      {stats.total_turmas || 0}
                    </p>
                  </div>
                  <Users className="h-8 w-8 text-purple-600" />
                </div>
              </CardContent>
            </Card>
  
            <Card className="stats-card">
            <CardContent className="p-6">
            <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-600">
              {user?.tipo === "admin"
              ? "Alunos"
               : user?.tipo === "instrutor"
              ? "Alunos no Curso"
              : "Alunos do Curso"}
            </p>
          <p className="text-2xl font-bold text-gray-900">
          {stats.total_alunos || 0}
            </p>
          { user?.tipo === "instrutor" && (
            <p className="text-xs text-gray-400 mt-1">
            Total no seu curso
            </p>
        )}
      </div>
          <UserCheck className="h-8 w-8 text-orange-600" />
      </div>
      </CardContent>
      </Card>
      </div>
          {/* Additional Stats Row */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <Card>
              
              <CardContent className="p-4">
                <div className="flex items-center space-x-2">
                  <CheckCircle className="h-5 w-5 text-green-500" />
                  <div>
                    <p className="text-sm text-gray-600">Alunos Ativos</p>
                    <p className="text-lg font-semibold">
                      {stats.alunos_ativos || 0}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
  
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center space-x-2">
                  <UserX className="h-5 w-5 text-red-500" />
                  <div>
                    <p className="text-sm text-gray-600">Desistentes</p>
                    <p className="text-lg font-semibold">
                      {stats.alunos_desistentes || 0}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
  
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center space-x-2">
                  <TrendingUp className="h-5 w-5 text-blue-500" />
                  <div>
                    <p className="text-sm text-gray-600">Taxa Presença</p>
                    <p className="text-lg font-semibold">
                      {stats.taxa_presenca_mes || 0}%
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
  
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center space-x-2">
                  <Calendar className="h-5 w-5 text-purple-500" />
                  <div>
                    <p className="text-sm text-gray-600">Chamadas Hoje</p>
                    <p className="text-lg font-semibold">
                      {stats.chamadas_hoje || 0}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
  
          {/* 🚀 PAINEL CHAMADAS PENDENTES - APENAS PARA INSTRUTORES */}
          {user?.tipo === "instrutor" && (
            <Card className="mb-8">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TriangleAlert className="h-5 w-5 text-orange-600" />
                  Chamadas Pendentes
                </CardTitle>
                <CardDescription>
                  {pendingLoading
                    ? "Carregando chamadas pendentes..."
                    : pending.length === 0
                      ? "✅ Todas as chamadas do dia foram realizadas!"
                      : `${pending.length} turma(s) sem chamada registrada para hoje`}
                </CardDescription>
              </CardHeader>
  
              <CardContent>
                {pendingLoading ? (
                  <div className="text-center py-4">
                    <RefreshCw className="h-6 w-6 animate-spin text-gray-400 mx-auto mb-2" />
                    <span className="text-gray-600">
                      Carregando chamadas pendentes...
                    </span>
                  </div>
                ) : pendingError ? (
                  <div className="text-center py-4 text-red-600">
                    <AlertCircle className="h-6 w-6 mx-auto mb-2" />
                    <span>Erro ao carregar: {pendingError}</span>
                    <Button
                      onClick={refetchPending}
                      variant="outline"
                      className="ml-2"
                    >
                      Tentar novamente
                    </Button>
                  </div>
                ) : pending.length === 0 ? (
                  <div className="text-center py-8 text-green-600">
                    <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-4" />
                    <p className="font-medium">
                      Todas as chamadas do dia foram realizadas!
                    </p>
                    <p className="text-sm text-gray-500 mt-2">
                      Não há turmas com chamadas pendentes.
                    </p>
                  </div>
                ) : (
                  <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                    {Array.isArray(pending) &&
                      pending.map((turma) => (
                        <PendingAttendanceCard
                          key={turma.turma_id}
                          turma={turma}
                          onComplete={markComplete}
                        />
                      ))}
                  </div>
                )}
              </CardContent>
            </Card>
          )}
                  {/* Management Tabs */}
                <Tabs defaultValue={user?.tipo === "gestor" ? "relatorios" : "turmas"} className="w-full">
                  <TabsList className="flex flex-wrap w-full justify-center gap-1 h-auto p-1">
                  {user?.tipo !== "gestor" && (
                    <TabsTrigger value="turmas" className="flex-1 min-w-0 text-sm whitespace-nowrap">
                      Turmas
                    </TabsTrigger>
                  )}
                  {user?.tipo !== "gestor" && (
                    <TabsTrigger value="chamada" className="flex-1 min-w-0 text-sm whitespace-nowrap">
                      Chamada
                    </TabsTrigger>
                  )}
                  {["admin", "instrutor", "pedagogo", "monitor","gestor"].includes(user?.tipo) && (
                    <TabsTrigger value="alunos" className="flex-1 min-w-0 text-sm whitespace-nowrap">
                      Alunos
                    </TabsTrigger>
                  )}
                  {user?.tipo === "admin" && (
                    <>
                      <TabsTrigger value="unidades" className="flex-1 min-w-0 text-sm whitespace-nowrap">
                        Unidades
                      </TabsTrigger>
                      <TabsTrigger value="cursos" className="flex-1 min-w-0 text-sm whitespace-nowrap">
                        Cursos
                      </TabsTrigger>
                      <TabsTrigger value="usuarios" className="flex-1 min-w-0 text-sm whitespace-nowrap">
                        Usuários
                      </TabsTrigger>
                    </>
                  )}
                  {user?.tipo === "admin" && (
                    <TabsTrigger value="solicitacoes" className="flex-1 min-w-0 text-sm whitespace-nowrap">
                    
                      Solicitações
                    </TabsTrigger>
                  )}
                  <TabsTrigger value="relatorios" className="flex-1 min-w-0 text-sm whitespace-nowrap">
                    
                    Relatórios
                  </TabsTrigger>
                </TabsList>
                    
              <TabsContent value="turmas">
              <TurmasManager filtros={filtrosTurmas} setFiltros={setFiltrosTurmas} />
            </TabsContent>
  
            <TabsContent value="chamada">
              <ChamadaManager />
            </TabsContent>
  
            {/* 🎯 ALUNOS: Instrutores/Pedagogos/Monitores podem cadastrar alunos em suas turmas */}
            {["admin", "instrutor", "pedagogo", "monitor"].includes(
              user?.tipo,
            ) && (
              <TabsContent value="alunos">
                <AlunosManager filtros={filtrosAlunos} setFiltros={setFiltrosAlunos} />
              </TabsContent>
            )}
  
            {user?.tipo === "admin" && (
              <>
                <TabsContent value="unidades">
                  <UnidadesManager />
                </TabsContent>
  
                <TabsContent value="cursos">
                  <CursosManager />
                </TabsContent>
  
                <TabsContent value="usuarios">
                  <UsuariosManager />
                </TabsContent>
              </>
            )}
  
              {user?.tipo === "admin" && (
                <TabsContent value="solicitacoes">
                  <AdminChangeRequestsPanel />
                  <div className="mt-6">
                    <AdminReactivationPanel />
                  </div>
                </TabsContent>
              )}

            <TabsContent value="relatorios">
              <RelatoriosManager />
            </TabsContent>
            </Tabs>
            </main>
  
        {/* Footer discreto */}
        <footer className="mt-auto py-4 border-t bg-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center text-xs text-gray-400">
              Desenvolvido por{" "}
              <span className="font-medium text-gray-600">Amaro's Developer</span>
            </div>
          </div>
        </footer>
      </div>
    );
  };
  
  // Sistema de Chamada Component CORRIGIDO
  const ChamadaManager = () => {
    const [turmas, setTurmas] = useState([]);
    const [selectedTurma, setSelectedTurma] = useState("");
    const [alunos, setAlunos] = useState([]);
    const [presencas, setPresencas] = useState({});
    const [observacoes, setObservacoes] = useState("");
    const [loading, setLoading] = useState(false);
    const [loadingAlunos, setLoadingAlunos] = useState(false);
    const [isAtestadoChamadaDialogOpen, setIsAtestadoChamadaDialogOpen] =
      useState(false);
    const [selectedAlunoAtestado, setSelectedAlunoAtestado] = useState(null);
    const [selectedFileAtestado, setSelectedFileAtestado] = useState(null);
  
    // Estados para modal de justificativa
    const [isChangeRequestOpen, setIsChangeRequestOpen] = useState(false);
    const [isJustificativaDialogOpen, setIsJustificativaDialogOpen] =
      useState(false);
    const [selectedAlunoJustificativa, setSelectedAlunoJustificativa] =
      useState(null);
    const [justificationReasons, setJustificationReasons] = useState([]);
    const [justificationForm, setJustificationForm] = useState({
      reason_code: "",
      observations: "",
      file: null,
    });
    const { toast } = useToast();
  
    useEffect(() => {
      fetchTurmas();
      fetchJustificationReasons();
    }, []);
  
    const fetchJustificationReasons = async () => {
      try {
        const response = await axios.get(`${API}/justifications/reasons`);
        const data = response.data;
  
        // Handle both array and object formats
        if (Array.isArray(data)) {
          setJustificationReasons(data);
        } else if (typeof data === "object" && data !== null) {
          // Convert object to array format
          const reasons = Object.entries(data).map(([code, label]) => ({
            code,
            label,
          }));
          setJustificationReasons(reasons);
        } else {
          setJustificationReasons([]);
        }
      } catch (error) {
        console.error("Erro ao carregar motivos de justificativa:", error);
        // Garantir que sempre é um array mesmo em caso de erro
        setJustificationReasons([]);
      }
    };
  
    const handleJustificarFalta = (aluno) => {
      setSelectedAlunoJustificativa(aluno);
      setJustificationForm({
        reason_code: "",
        observations: "",
        file: null,
      });
      setIsJustificativaDialogOpen(true);
    };
  
    const submitJustificativa = async () => {
      if (!justificationForm.reason_code) {
        toast({
          title: "Erro",
          description: "Selecione um motivo para a justificativa",
          variant: "destructive",
        });
        return;
      }
  
      try {
        const formData = new FormData();
        formData.append("reason_code", justificationForm.reason_code);
        if (justificationForm.observations) {
          formData.append("reason_text", justificationForm.observations);
          formData.append("observations", justificationForm.observations);
        }
        if (justificationForm.file) {
          formData.append("file", justificationForm.file);
        }
        
        await axios.post(
          `${API}/students/${selectedAlunoJustificativa.id}/justifications`,
          formData,
          {
            headers: {
              "Content-Type": "multipart/form-data",
            },
            timeout: 30000,
          },
        );
  
        // Marcar falta como justificada na presença
        const updatedPresencas = {
          ...presencas,
          [selectedAlunoJustificativa.id]: {
            ...presencas[selectedAlunoJustificativa.id],
            presente: false,
            justificativa: `Falta justificada: ${
              (Array.isArray(justificationReasons) &&
                justificationReasons.find(
                  (r) => r.code === justificationForm.reason_code,
                )?.label) ||
              justificationForm.reason_code
            }`,
          },
        };
        setPresencas(updatedPresencas);
  
        toast({
          title: "Sucesso",
          description: "Justificativa registrada com sucesso!",
        });
  
        setIsJustificativaDialogOpen(false);
      } catch (error) {
        console.error("Erro ao registrar justificativa:", error);
        toast({
          title: "Erro",
          description: "Erro ao registrar justificativa",
          variant: "destructive",
        });
      }
    };
  
    const fetchTurmas = async () => {
      try {
        setLoading(true);
        const response = await axios.get(`${API}/classes`);
        // Garantir que response.data é um array
        const turmasData = Array.isArray(response.data) ? response.data : [];
        setTurmas(turmasData);
      } catch (error) {
        console.error("Error fetching turmas:", error);
        setTurmas([]); // Garantir que turmas seja sempre um array
      } finally {
        setLoading(false);
      }
    };
  
    const fetchAlunos = async (turmaId) => {
      try {
        setLoadingAlunos(true);
        console.log("Fetching alunos for turma:", turmaId);
        const response = await axios.get(`${API}/classes/${turmaId}/students`);
        console.log("Alunos response:", response.data);
  
        // Garantir que response.data é um array
        const alunosData = Array.isArray(response.data) ? response.data : [];
        setAlunos(alunosData);
  
        // Initialize presencas with all students present by default
        const initialPresencas = {};
        alunosData.forEach((aluno) => {
          initialPresencas[aluno.id] = {
            presente: true,
            justificativa: "",
            atestado_id: "",
          };
        });
        setPresencas(initialPresencas);
      } catch (error) {
        console.error("Error fetching alunos:", error);
        toast({
          title: "Erro ao carregar alunos",
          description: "Não foi possível carregar a lista de alunos da turma",
          variant: "destructive",
        });
      } finally {
        setLoadingAlunos(false);
      }
    };
  
    const handleTurmaChange = (turmaId) => {
      debugLog("ChamadaManager: Turma selected", {
        turmaId,
        previousTurma: selectedTurma,
      });
  
      try {
        setSelectedTurma(turmaId);
        setAlunos([]);
        setPresencas({});
        if (turmaId) {
          fetchAlunos(turmaId);
        }
      } catch (error) {
        debugLog("ChamadaManager: ERROR in handleTurmaChange", {
          error: error.message,
          turmaId,
        });
        console.error("Erro em handleTurmaChange:", error);
      }
    };
  
    const handlePresencaChange = (alunoId, presente) => {
      setPresencas((prev) => ({
        ...prev,
        [alunoId]: {
          ...prev[alunoId],
          presente,
        },
      }));
    };
  
    const handleJustificativaChange = (alunoId, justificativa) => {
      setPresencas((prev) => ({
        ...prev,
        [alunoId]: {
          ...prev[alunoId],
          justificativa,
        },
      }));
    };
  
    const handleUploadAtestadoChamada = (aluno) => {
      setSelectedAlunoAtestado(aluno);
      setSelectedFileAtestado(null);
      setIsAtestadoChamadaDialogOpen(true);
    };
  
    const submitAtestadoChamada = async () => {
      if (!selectedFileAtestado) {
        toast({
          title: "Arquivo obrigatório",
          description: "Por favor, selecione um arquivo de atestado.",
          variant: "destructive",
        });
        return;
      }
  
      try {
        const formData = new FormData();
        formData.append("file", selectedFileAtestado);
        formData.append("aluno_id", selectedAlunoAtestado.id);
        formData.append("tipo", "atestado_medico");
  
        const response = await axios.post(`${API}/upload/atestado`, formData, {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        });
  
        // Atualizar a presença com o ID do atestado
        setPresencas((prev) => ({
          ...prev,
          [selectedAlunoAtestado.id]: {
            ...prev[selectedAlunoAtestado.id],
            atestado_id: response.data.id,
            justificativa: "Falta justificada com atestado médico",
          },
        }));
  
        toast({
          title: "Atestado enviado",
          description: `Atestado médico de ${selectedAlunoAtestado.nome} foi registrado na chamada.`,
        });
  
        setIsAtestadoChamadaDialogOpen(false);
        setSelectedAlunoAtestado(null);
        setSelectedFileAtestado(null);
      } catch (error) {
        console.error("Error uploading atestado:", error);
        toast({
          title: "Erro ao enviar atestado",
          description: error.response?.data?.detail || "Tente novamente",
          variant: "destructive",
        });
      }
    };
  
    const handleSalvarChamada = async () => {
      debugLog("ChamadaManager: Iniciando salvamento de chamada", {
        selectedTurma,
        totalAlunos: alunos.length,
        totalPresencas: Object.keys(presencas).length,
      });
  
      if (!selectedTurma) {
        debugLog("ChamadaManager: ERROR - Nenhuma turma selecionada");
        toast({
          title: "Erro",
          description: "Selecione uma turma primeiro",
          variant: "destructive",
        });
        return;
      }
  
      // 🔒 VALIDAÇÃO: Só permite chamada do dia atual
      const hoje = new Date().toISOString().split("T")[0];
      const agora = new Date().toTimeString().split(" ")[0].substring(0, 5);
  
      // Verificar se é realmente hoje
      const dataAtual = new Date();
      const dataHoje = dataAtual.toISOString().split("T")[0];
  
      if (hoje !== dataHoje) {
        debugLog("ChamadaManager: ERROR - Data inválida", { hoje, dataHoje });
        toast({
          title: "Data inválida",
          description: "Só é possível fazer chamada da data atual",
          variant: "destructive",
        });
        return;
      }
  
      try {
        debugLog("ChamadaManager: Enviando dados para API", {
          endpoint: `${API}/attendance`,
          data: { turma_id: selectedTurma, data: hoje, horario: agora },
        });
  
        await axios.post(`${API}/attendance`, {
          turma_id: selectedTurma,
          data: hoje,
          horario: agora,
          observacoes_aula: observacoes,
          presencas: presencas,
        });
  
        debugLog(
          "ChamadaManager: Chamada salva com sucesso - iniciando limpeza de estados",
        );
  
        toast({
          title: "Chamada salva com sucesso!",
          description: `Os dados de presença foram registrados para ${new Date().toLocaleDateString(
            "pt-BR",
          )}`,
        });
  
        // 🎯 CORREÇÃO CRÍTICA: Salvar ID da turma antes de limpar estados
        const turmaIdParaRemover = selectedTurma;
        debugLog("ChamadaManager: Turma ID salvo para remoção", {
          turmaIdParaRemover,
        });
  
        // ⚡ PROTEÇÃO REACT DOM: Limpeza sequencial com delays maiores
        const clearStatesSequentially = () => {
          debugLog(
            "ChamadaManager: Iniciando limpeza sequencial (VERSÃO CORRIGIDA)",
          );
  
          // 1. Limpar seleção primeiro
          setSelectedTurma("");
  
          // 2. Aguardar renderização antes de limpar outros estados (delay aumentado)
          setTimeout(() => {
            debugLog("ChamadaManager: Limpando demais estados", {
              alunosCount: alunos.length,
              presencasCount: Object.keys(presencas).length,
            });
  
            setAlunos([]);
            setPresencas({});
            setObservacoes("");
  
            // 3. Aguardar mais tempo antes de modificar lista de turmas
            setTimeout(() => {
              debugLog("ChamadaManager: Removendo turma da lista", {
                turmaIdParaRemover,
              });
              setTurmas((prev) => {
                const novaLista = prev.filter((t) => t.id !== turmaIdParaRemover);
                debugLog("ChamadaManager: Turma removida da lista", {
                  antes: prev.length,
                  depois: novaLista.length,
                });
                return novaLista;
              });
            }, 50); // Delay muito maior para garantir estabilidade do DOM
          }, 20);
        };
  
        // Executar limpeza com proteção adicional
        try {
          clearStatesSequentially();
        } catch (domError) {
          debugLog("ChamadaManager: ERRO DOM CAPTURADO durante limpeza", {
            error: domError.message,
            stack: domError.stack,
          });
  
          // Fallback: tentar novamente após delay maior
          setTimeout(() => {
            debugLog("ChamadaManager: Tentativa de limpeza após erro DOM");
            try {
              setSelectedTurma("");
              setAlunos([]);
              setPresencas({});
              setObservacoes("");
              setTurmas((prev) =>
                prev.filter((t) => t.id !== turmaIdParaRemover),
              );
            } catch (secondError) {
              debugLog("ChamadaManager: SEGUNDO ERRO DOM - fallback falhou", {
                error: secondError.message,
              });
            }
          }, 100);
        }
      } catch (error) {
        debugLog("ChamadaManager: ERROR ao salvar chamada", {
          error: error.message,
          status: error.response?.status,
          detail: error.response?.data?.detail,
        });
  
        toast({
          title: "Erro ao salvar chamada",
          description:
            error.response?.data?.detail ||
            "Já foi feita chamada hoje para esta turma",
          variant: "destructive",
        });
      }
    };
  
    const totalPresentes = Object.values(presencas).filter(
      (p) => p.presente,
    ).length;
    const totalFaltas = Object.values(presencas).filter(
      (p) => !p.presente,
    ).length;
  
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <UserCheck className="h-5 w-5 mr-2 text-blue-600" />
            Sistema de Chamada
          </CardTitle>
          <CardDescription>
            Registre a presença dos alunos de forma rápida e eficiente
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-2">
            <Label>Selecionar Turma</Label>
            <Select value={selectedTurma} onValueChange={handleTurmaChange}>
              <SelectTrigger>
                <SelectValue placeholder="Selecione uma turma" />
              </SelectTrigger>
              <SelectContent>
                {Array.isArray(turmas) &&
                  turmas.map((turma) => (
                    <SelectItem key={turma.id} value={turma.id}>
                      {turma.nome} - {turma.ciclo}
                    </SelectItem>
                  ))}
              </SelectContent>
            </Select>
          </div>
  
          {selectedTurma &&
            Array.isArray(turmas) &&
            turmas.find((t) => t.id === selectedTurma) && (
              <div className="grid grid-cols-3 gap-4">
                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center space-x-2">
                      <Users className="h-5 w-5 text-blue-500" />
                      <div>
                        <p className="text-sm text-gray-600">Total de Alunos</p>
                        <p className="text-lg font-semibold">{alunos.length}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
  
                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center space-x-2">
                      <CheckCircle className="h-5 w-5 text-green-500" />
                      <div>
                        <p className="text-sm text-gray-600">Presentes</p>
                        <p className="text-lg font-semibold text-green-600">
                          {totalPresentes}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
  
                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center space-x-2">
                      <AlertCircle className="h-5 w-5 text-red-500" />
                      <div>
                        <p className="text-sm text-gray-600">Faltas</p>
                        <p className="text-lg font-semibold text-red-600">
                          {totalFaltas}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}
  
          {loadingAlunos && (
            <div className="text-center py-8">
              <div className="loading-spinner mx-auto mb-4"></div>
              <p>Carregando lista de alunos...</p>
            </div>
          )}
  
          {alunos.length > 0 && !loadingAlunos && (
            <>
              <div className="space-y-4">
                <h3 className="text-lg font-semibold flex items-center">
                  <Users className="h-5 w-5 mr-2" />
                  Lista de Presença - {new Date().toLocaleDateString()}
                </h3>
  
                <div className="space-y-3">
                  {Array.isArray(alunos) &&
                    alunos.map((aluno, index) => (
                      <Card
                        key={aluno.id}
                        className={`p-4 transition-all ${
                          presencas[aluno.id]?.presente
                            ? "border-green-200 bg-green-50"
                            : "border-red-200 bg-red-50"
                        }`}
                      >
                        <div className="flex items-start space-x-4">
                          <div className="flex items-center space-x-3">
                            <span className="font-mono text-sm text-gray-500 w-8">
                              {String(index + 1).padStart(2, "0")}
                            </span>
                            <div className="flex items-center space-x-2">
                              <Checkbox
                                checked={presencas[aluno.id]?.presente || false}
                                onCheckedChange={(checked) =>
                                  handlePresencaChange(aluno.id, checked)
                                }
                                className="w-5 h-5"
                              />
                              <label className="text-sm font-medium cursor-pointer">
                                {presencas[aluno.id]?.presente
                                  ? "Presente"
                                  : "Falta"}
                              </label>
                            </div>
                          </div>
  
                          <div className="flex-1">
                            <p className="font-medium">{aluno.nome_social || aluno.nome || `CPF: ${aluno.cpf}` || "Aluno sem nome"}</p>
                            <p className="text-sm text-gray-500">
                              CPF: {aluno.cpf}
                            </p>
                          </div>
  
                          {!presencas[aluno.id]?.presente && (
                            <div className="flex-1 space-y-2">
                              <div className="flex items-center justify-between">
                                <Label className="text-sm">
                                  Justificativa da Falta
                                </Label>
                                <Button
                                  onClick={() => handleJustificarFalta(aluno)}
                                  variant="outline"
                                  size="sm"
                                  className="h-8"
                                >
                                  <FileText className="h-4 w-4 mr-1" />
                                  Justificar com Documento
                                </Button>
                              </div>
                              <Textarea
                                placeholder="Digite o motivo da falta..."
                                value={presencas[aluno.id]?.justificativa || ""}
                                onChange={(e) =>
                                  handleJustificativaChange(
                                    aluno.id,
                                    e.target.value,
                                  )
                                }
                                className="min-h-16"
                              />
                            </div>
                          )}
                        </div>
                      </Card>
                    ))}
                </div>
              </div>
  
              <div className="space-y-2">
                <Label htmlFor="observacoes">Observações da Aula</Label>
                <Textarea
                  id="observacoes"
                  placeholder="Digite observações sobre a aula, conteúdo ministrado, ocorrências..."
                  value={observacoes}
                  onChange={(e) => setObservacoes(e.target.value)}
                />
              </div>
  
              <Button
                onClick={handleSalvarChamada}
                className="w-full bg-green-600 hover:bg-green-700 h-12 text-lg"
              >
                <Save className="h-5 w-5 mr-2" />
                Salvar Chamada - {totalPresentes} Presentes, {totalFaltas} Faltas
              </Button>
            </>
          )}
  
            {selectedTurma && alunos.length === 0 && !loadingAlunos && (
            <div className="text-center py-8 text-gray-500">
              <Users className="h-12 w-12 mx-auto mb-4 text-gray-300" />
              <p>Nenhum aluno encontrado nesta turma</p>
            </div>
          )}

          {/* Botão para solicitar correção de chamada anterior */}
          <div className="mt-4 pt-4 border-t border-gray-200">
            <Button
              variant="outline"
              onClick={() => setIsChangeRequestOpen(true)}
              className="w-full border-orange-400 text-orange-600 hover:bg-orange-50"
            >
              <Edit className="h-4 w-4 mr-2" />
              Solicitar Correção de Chamada Anterior
            </Button>
            <p className="text-xs text-gray-400 mt-2 text-center">
              Errou ao marcar presença ou falta em um dia anterior? Solicite a
              correção ao administrador.
            </p>
          </div>

          <AttendanceChangeRequestModal
            open={isChangeRequestOpen}
            onClose={() => setIsChangeRequestOpen(false)}
          />
        </CardContent>
  
        {/* Dialog para upload de atestado na chamada */}
        <Dialog
          open={isAtestadoChamadaDialogOpen}
          onOpenChange={setIsAtestadoChamadaDialogOpen}
        >
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Upload Atestado Médico</DialogTitle>
              <DialogDescription>
                Anexar atestado médico para {selectedAlunoAtestado?.nome}
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label>Arquivo do atestado *</Label>
                <Input
                  type="file"
                  accept=".pdf,.jpg,.jpeg,.png"
                  onChange={(e) => setSelectedFileAtestado(e.target.files[0])}
                />
                <p className="text-sm text-gray-500 mt-1">
                  Formatos aceitos: PDF, JPG, PNG (máx. 5MB)
                </p>
              </div>
              <div className="flex justify-end space-x-2">
                <Button
                  variant="outline"
                  onClick={() => setIsAtestadoChamadaDialogOpen(false)}
                >
                  Cancelar
                </Button>
                <Button
                  onClick={submitAtestadoChamada}
                  className="bg-green-600 hover:bg-green-700"
                >
                  <Upload className="h-4 w-4 mr-2" />
                  Anexar Atestado
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
  
        {/* Dialog para justificativa de falta */}
        <Dialog
          open={isJustificativaDialogOpen}
          onOpenChange={setIsJustificativaDialogOpen}
        >
          <DialogContent className="max-w-md">
            <DialogHeader>
              <DialogTitle className="flex items-center">
                <FileText className="h-5 w-5 mr-2" />
                Justificar Falta
              </DialogTitle>
              <DialogDescription>
                Registrar justificativa para {selectedAlunoJustificativa?.nome}
              </DialogDescription>
            </DialogHeader>
  
            <div className="space-y-4">
              {/* Motivo da justificativa */}
              <div className="space-y-2">
                <Label className="text-sm font-medium flex items-center">
                  <AlertCircle className="h-4 w-4 mr-1" />
                  Motivo da falta *
                </Label>
                <Select
                  value={justificationForm.reason_code}
                  onValueChange={(value) =>
                    setJustificationForm((prev) => ({
                      ...prev,
                      reason_code: value,
                    }))
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Selecione o motivo" />
                  </SelectTrigger>
                  <SelectContent>
                    {Array.isArray(justificationReasons) &&
                      justificationReasons.map((reason) => (
                        <SelectItem key={reason.code} value={reason.code}>
                          {reason.label}
                        </SelectItem>
                      ))}
                  </SelectContent>
                </Select>
              </div>
  
              {/* Observações */}
              <div className="space-y-2">
                <Label className="text-sm font-medium">Observações</Label>
                <Textarea
                  placeholder="Observações adicionais sobre a falta..."
                  value={justificationForm.observations}
                  onChange={(e) =>
                    setJustificationForm((prev) => ({
                      ...prev,
                      observations: e.target.value,
                    }))
                  }
                  className="min-h-20"
                />
              </div>
  
              {/* Upload de arquivo */}
              <div className="space-y-2">
                <Label className="text-sm font-medium">
                  Documento (opcional)
                </Label>
                <Input
                  type="file"
                  accept=".pdf,.jpg,.jpeg,.png"
                  onChange={(e) =>
                    setJustificationForm((prev) => ({
                      ...prev,
                      file: e.target.files[0],
                    }))
                  }
                />
                <p className="text-xs text-gray-500">
                  Formatos aceitos: PDF, JPG, PNG (máx. 5MB)
                </p>
              </div>
  
              {/* Botões */}
              <div className="flex justify-end space-x-2 pt-4">
                <Button
                  variant="outline"
                  onClick={() => setIsJustificativaDialogOpen(false)}
                >
                  Cancelar
                </Button>
                <Button
                  onClick={submitJustificativa}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  <FileText className="h-4 w-4 mr-2" />
                  Registrar Justificativa
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </Card>
    );
  };
  
  // Usuarios Manager Component CORRIGIDO
const UsuariosManager = () => {
  const [usuarios, setUsuarios] = useState([]);
  const [unidades, setUnidades] = useState([]);
  const [cursos, setCursos] = useState([]);
  const [pendingUsers, setPendingUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingUser, setEditingUser] = useState(null);

  // ALTERAÇÃO 10/04/2026 — Adicionados arrays para suportar múltiplas unidades/cursos por professor e titulo personalizavel 
  const [formData, setFormData] = useState({
    nome: "",
    email: "",
    tipo: "",
    telefone: "",
    unidade_id: "",
    curso_id: "",
    unidade_ids: [],
    curso_ids: [],
    titulo_personalizado: "",
  });

  // CORREÇÃO: useToast declarado no topo para ser usado em todo o componente
  const { toast } = useToast();

  // Daqui para baixo você continua com suas funções (fetchData, handleSubmit, etc...)
    useEffect(() => {
      fetchData();
    }, []);
  
    // 🚀 FUNÇÃO PING PARA ACORDAR RENDER
    const wakeUpBackend = async () => {
      console.log("🔔 Acordando backend Render...");
      try {
        const pingResponse = await axios.get(`${API}/ping`, { timeout: 30000 });
        console.log("✅ Backend acordado:", pingResponse.data);
        return true;
      } catch (error) {
        console.error("❌ Erro ao acordar backend:", error);
        return false;
      }
    };
  
    const fetchData = async () => {
      try {
        // 🚀 PRIMEIRO: Acordar o backend
        const backendAwake = await wakeUpBackend();
        if (!backendAwake) {
          console.warn(
            "⚠️ Backend pode estar dormindo, tentando requisições diretas...",
          );
        }
  
        const [usuariosRes, unidadesRes, cursosRes] = await Promise.all([
          axios.get(`${API}/users`),
          axios.get(`${API}/units`),
          axios.get(`${API}/courses`),
        ]);
  
        setUsuarios(Array.isArray(usuariosRes.data) ? usuariosRes.data : []);
        setUnidades(Array.isArray(unidadesRes.data) ? unidadesRes.data : []);
        setCursos(Array.isArray(cursosRes.data) ? cursosRes.data : []);
  
        // Fetch pending users
        try {
          const pendingRes = await axios.get(`${API}/users/pending`);
          setPendingUsers(Array.isArray(pendingRes.data) ? pendingRes.data : []);
        } catch (error) {
          console.error("Error fetching pending users:", error);
          setPendingUsers([]);
        }
      } catch (error) {
        console.error("Error fetching data:", error);
        setUsuarios([]);
        setUnidades([]);
        setCursos([]);
        setPendingUsers([]);
      } finally {
        setLoading(false);
      }
    };
  
    const handleSubmit = async (e) => {
      e.preventDefault();
      try {
  if (editingUser) {
    await axios.put(`${API}/users/${editingUser.id}`, {
      nome: formData.nome,
      email: formData.email,
      tipo: formData.tipo,
      telefone: formData.telefone,
      unidade_id: formData.unidade_id,
      curso_id: formData.curso_id,
      // ALTERAÇÃO 27/03/2026 — Enviar arrays novos ao backend.
      // O backend aceita ambos os formatos (singular + array)
      unidade_ids: formData.unidade_ids,
      curso_ids: formData.curso_ids,
    });      
    toast({
      title: "Usuário atualizado com sucesso!",
      description: "As informações do usuário foram atualizadas.",
      });
     }else{
          // When creating user, a temporary password will be generated
          await axios.post(`${API}/users`, formData);
          toast({
            title: "Usuário criado com sucesso!",
            description:
              "Uma senha temporária foi gerada. O usuário deve fazer login e alterá-la.",
          });
        }
  
        // Fechar modal primeiro
        setIsDialogOpen(false);
  
        // Aguardar o modal fechar antes de atualizar estados
        setTimeout(() => {
          setEditingUser(null);
          resetForm();
          fetchData();
        }, 100);
      } catch (error) {
        toast({
          title: editingUser
            ? "Erro ao atualizar usuário"
            : "Erro ao criar usuário",
          description: error.response?.data?.detail || "Tente novamente",
          variant: "destructive",
        });
      }
    };
  
    // 🔐 NOVA FUNÇÃO: Reset de senha administrativo
    const handleResetPassword = async (userId, userName) => {
      try {
        const response = await axios.post(
          `${API}/users/${userId}/reset-password`,
        );
  
        toast({
          title: "Senha resetada com sucesso!",
          description: `Nova senha temporária para ${response.data.user_name}: ${response.data.temp_password}`,
          variant: "default",
        });
  
        // Mostra alert adicional para garantir que admin veja a senha
        alert(
          `🔐 SENHA TEMPORÁRIA para ${response.data.user_name}:\n\n${response.data.temp_password}\n\nInforme esta senha ao usuário. Ele deverá alterá-la no primeiro acesso.`,
        );
      } catch (error) {
        toast({
          title: "Erro ao resetar senha",
          description: error.response?.data?.detail || "Tente novamente",
          variant: "destructive",
        });
      }
    };
  
    const handleApproveUser = async (userId) => {
      try {
        await axios.put(`${API}/users/${userId}/approve`);
        toast({
          title: "Usuário aprovado!",
          description: "O usuário pode agora acessar o sistema.",
        });
        fetchData();
      } catch (error) {
        toast({
          title: "Erro ao aprovar usuário",
          description: error.response?.data?.detail || "Tente novamente",
          variant: "destructive",
        });
      }
    };
  
  const resetForm = () => {
    setFormData({
      nome: "",
      email: "",
      tipo: "",
      telefone: "",
      unidade_id: "",
      curso_id: "",
      unidade_ids: [],
      curso_ids: [],
      titulo_personalizado: "",
    });
  };
    const handleEdit = (usuario) => {
    setEditingUser(usuario);
    setFormData({
      nome: usuario.nome,
      email: usuario.email,
      tipo: usuario.tipo,
      telefone: usuario.telefone || "",
      unidade_id: usuario.unidade_id || "",
      curso_id: usuario.curso_id || "",
      unidade_ids: usuario.unidade_ids?.length > 0
        ? usuario.unidade_ids
        : (usuario.unidade_id ? [usuario.unidade_id] : []),
      curso_ids: usuario.curso_ids?.length > 0
        ? usuario.curso_ids
        : (usuario.curso_id ? [usuario.curso_id] : []),
      titulo_personalizado: usuario.titulo_personalizado || "",
    });
    setIsDialogOpen(true);
  };
  
    const handleDelete = async (userId) => {
      if (window.confirm("Tem certeza que deseja desativar este usuário?")) {
        try {
          await axios.delete(`${API}/users/${userId}`);
          toast({
            title: "Usuário desativado com sucesso!",
            description: "O usuário foi desativado do sistema.",
          });
          fetchData();
        } catch (error) {
          toast({
            title: "Erro ao desativar usuário",
            description: error.response?.data?.detail || "Tente novamente",
            variant: "destructive",
          });
        }
      }
    };
  
    const handleOpenDialog = () => {
      setEditingUser(null);
      resetForm();
      setIsDialogOpen(true);
    };
  
    // Função removida - usando getUserTypeLabel global com nomenclatura unissex
  
    if (loading)
      return (
        <div key="usuarios-loading" className="p-8 text-center">
          Carregando usuários...
        </div>
      );
  
    return (
      <div key="usuarios-content" className="space-y-6">
        {/* Pending Users Section */}
        {pendingUsers.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Shield className="h-5 w-5 mr-2 text-orange-500" />
                Usuários Pendentes de Aprovação
              </CardTitle>
              <CardDescription>
                Usuários que solicitaram primeiro acesso e aguardam aprovação
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {Array.isArray(pendingUsers) &&
                  pendingUsers.map((user) => (
                    <div
                      key={user.id}
                      className="flex items-center justify-between p-4 border rounded-lg"
                    >
                      <div>
                        <p className="font-medium">{user.nome}</p>
                        <p className="text-sm text-gray-500">
                          {user.email} - {getUserTypeLabel(user.tipo)}
                        </p>
                      </div>
                      <Button
                        onClick={() => handleApproveUser(user.id)}
                        className="bg-green-600 hover:bg-green-700"
                      >
                        <CheckCircle className="h-4 w-4 mr-2" />
                        Aprovar
                      </Button>
                    </div>
                  ))}
              </div>
            </CardContent>
          </Card>
        )}
  
        {/* Users Management */}
        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <div>
                <CardTitle>Gerenciamento de Usuários</CardTitle>
                <CardDescription>
                  Gerencie usuários do sistema (Administrador(a), Professor(a),
                  Coord. Pedagógico, Assistente)
                </CardDescription>
              </div>
              <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
                <DialogTrigger asChild>
                  <Button
                    onClick={handleOpenDialog}
                    className="bg-blue-600 hover:bg-blue-700"
                  >
                    <Plus className="h-4 w-4 mr-2" />
                    Novo Usuário
                  </Button>
                </DialogTrigger>
                <DialogContent className="max-w-md max-h-[90vh] overflow-y-auto">
                  <DialogHeader>
                    <DialogTitle>
                      {editingUser ? "Editar Usuário" : "Criar Novo Usuário"}
                    </DialogTitle>
                    <DialogDescription>
                      {editingUser
                        ? "Atualize os dados do usuário"
                        : "Preencha os dados para criar um novo usuário. Uma senha temporária será gerada."}
                    </DialogDescription>
                  </DialogHeader>
                  <form onSubmit={handleSubmit} className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="nome">Nome Completo</Label>
                      <Input
                        id="nome"
                        value={formData.nome}
                        onChange={(e) =>
                          setFormData({ ...formData, nome: e.target.value })
                        }
                        required
                      />
                    </div>
  
                    <div className="space-y-2">
                      <Label htmlFor="email">Email</Label>
                      <Input
                        id="email"
                        type="email"
                        value={formData.email}
                        onChange={(e) =>
                          setFormData({ ...formData, email: e.target.value })
                        }
                        required
                      />
                    </div>
  
                    <div className="space-y-2">
                      <Label>Tipo de Usuário</Label>
                      <Select
                        value={formData.tipo}
                        onValueChange={(value) =>
                          setFormData({ ...formData, tipo: value })
                        }
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Selecione o tipo de usuário" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="admin">
                            {getUserTypeLabel("admin")}
                          </SelectItem>
                          <SelectItem value="instrutor">
                            {getUserTypeLabel("instrutor")}
                          </SelectItem>
                          <SelectItem value="pedagogo">
                            {getUserTypeLabel("pedagogo")}
                          </SelectItem>
                          <SelectItem value="monitor">
                            {getUserTypeLabel("monitor")}
                          </SelectItem>
                          <SelectItem value="gestor">
                            {getUserTypeLabel("gestor")}
                          </SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                          
                    <div className="space-y-2">
                      <Label htmlFor="telefone">Telefone</Label>
                      <Input
                        id="telefone"
                        value={formData.telefone}
                        onChange={(e) =>
                          setFormData({ ...formData, telefone: e.target.value })
                        }
                        placeholder="(11) 99999-9999"
                      />
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor="titulo_personalizado">
                        Título de exibição (opcional)
                      </Label>
                      <Input
                        id="titulo_personalizado"
                        value={formData.titulo_personalizado}
                        onChange={(e) =>
                          setFormData({ ...formData, titulo_personalizado: e.target.value })
                        }
                        placeholder={
                          formData.tipo
                            ? `Padrão: ${getUserTypeLabel(formData.tipo)}`
                            : "Selecione o tipo primeiro"
                        }
                      />
                      <p className="text-xs text-gray-500">
                        Personalize o título exibido. Ex: Coordenador(a), Supervisor(a)
                      </p>
                    </div>


                    {formData.tipo !== "admin" && (
                      <>
                        <div className="space-y-2">
                          <Label>
                            {editingUser ? "Unidades (pode selecionar várias)" : "Unidade"}
                          </Label>
                          {editingUser ? (
                            <div className="border rounded-lg p-2 space-y-1 max-h-40 overflow-y-auto">
                              {Array.isArray(unidades) && unidades.map((unidade) => (
                                <div key={unidade.id} className="flex items-center space-x-2">
                                  <Checkbox
                                    id={`unidade-${unidade.id}`}
                                    checked={(formData.unidade_ids || []).map(String).includes(String(unidade.id))}
                                    onCheckedChange={(checked) => {
                                      const atual = formData.unidade_ids || [];
                                      const novos = checked
                                        ? [...atual, unidade.id]
                                        : atual.filter(id => String(id) !== String(unidade.id));
                                      setFormData({
                                        ...formData,
                                        unidade_ids: novos,
                                        unidade_id: novos[0] || "",
                                      });
                                    }}
                                  />
                                  <label htmlFor={`unidade-${unidade.id}`} className="text-sm cursor-pointer">
                                    {unidade.nome}
                                  </label>
                                </div>
                              ))}
                            </div>
                          ) : (
                            <Select
                              value={formData.unidade_id}
                              onValueChange={(value) => setFormData({ ...formData, unidade_id: value })}
                            >
                              <SelectTrigger>
                                <SelectValue placeholder="Selecione a unidade" />
                              </SelectTrigger>
                              <SelectContent>
                                {Array.isArray(unidades) && unidades.map((unidade) => (
                                  <SelectItem key={unidade.id} value={unidade.id}>
                                    {unidade.nome}
                                  </SelectItem>
                                ))}
                              </SelectContent>
                            </Select>
                          )}
                        </div>
                    
                        {["instrutor", "pedagogo", "monitor"].includes(formData.tipo) && (
                          <div className="space-y-2">
                            <Label>
                              {editingUser ? "Cursos (pode selecionar várias)" : "Curso *"}
                            </Label>
                            {editingUser ? (
                              <div className="border rounded-lg p-2 space-y-1 max-h-40 overflow-y-auto">
                                {Array.isArray(cursos) && cursos.map((curso) => (
                                  <div key={curso.id} className="flex items-center space-x-2">
                                    <Checkbox
                                      id={`curso-${curso.id}`}
                                      checked={(formData.curso_ids || []).map(String).includes(String(curso.id))}
                                      onCheckedChange={(checked) => {
                                        const atual = formData.curso_ids || [];
                                        const novos = checked
                                          ? [...atual, curso.id]
                                          : atual.filter(id => String(id) !== String(curso.id));
                                        setFormData({
                                          ...formData,
                                          curso_ids: novos,
                                          curso_id: novos[0] || "",
                                        });
                                      }}
                                    />
                                    <label htmlFor={`curso-${curso.id}`} className="text-sm cursor-pointer">
                                      {curso.nome}
                                    </label>
                                  </div>
                                ))}
                              </div>
                            ) : (
                              <Select
                                value={formData.curso_id}
                                onValueChange={(value) => setFormData({ ...formData, curso_id: value })}
                              >
                                <SelectTrigger>
                                  <SelectValue placeholder="Selecione o curso" />
                                </SelectTrigger>
                                <SelectContent>
                                  {Array.isArray(cursos) && cursos.map((curso) => (
                                    <SelectItem key={curso.id} value={curso.id}>
                                      {curso.nome}
                                    </SelectItem>
                                  ))}
                                </SelectContent>
                              </Select>
                            )}
                          </div>
                        )}
                      </>
                    )} 
                    <Button
                      type="submit"
                      className="w-full bg-blue-600 hover:bg-blue-700"
                    >
                      <Save className="h-4 w-4 mr-2" />
                      {editingUser ? "Atualizar Usuário" : "Criar Usuário"}
                    </Button>
                  </form>
                </DialogContent>
              </Dialog>
            </div>
          </CardHeader>
          <CardContent>
            <div className="table-container">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Nome</TableHead>
                    <TableHead>Email</TableHead>
                    <TableHead>Tipo</TableHead>
                    <TableHead>Telefone</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Ações</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {Array.isArray(usuarios) &&
                    usuarios.map((usuario) => (
                      <TableRow key={usuario.id}>
                        <TableCell className="font-medium">
                          {usuario.nome}
                        </TableCell>
                        <TableCell>{usuario.email}</TableCell>
                        <TableCell>
                          <Badge variant="outline">
                            {getUserTypeLabel(usuario.tipo)}
                          </Badge>
                        </TableCell>
                        <TableCell>{usuario.telefone || "-"}</TableCell>
                        <TableCell>
                          <Badge
                            variant={usuario.ativo ? "default" : "secondary"}
                          >
                            {usuario.ativo ? "Ativo" : "Inativo"}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <div className="flex space-x-2">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleEdit(usuario)}
                            >
                              <Edit className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() =>
                                handleResetPassword(usuario.id, usuario.nome)
                              }
                              className="text-blue-600 hover:text-blue-700"
                              title="Resetar Senha"
                            >
                              <Key className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleDelete(usuario.id)}
                              className="text-red-600 hover:text-red-700"
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  };
    
    // 🔍 COMPONENTE: Gerenciador de Alunos dentro da Turma (com busca)
    const AlunosTurmaManager = ({ selectedTurmaForAlunos, alunos, onAdd, onRemove }) => {
      const [buscaDisponivel, setBuscaDisponivel] = useState("");
      const [buscaNaTurma, setBuscaNaTurma] = useState("");
    
      const alunosNaTurma = alunos.filter((aluno) =>
        selectedTurmaForAlunos?.alunos_ids?.includes(aluno.id)
      );
    
      const alunosDisponiveis = alunos.filter(
        (aluno) =>
          !selectedTurmaForAlunos?.alunos_ids?.includes(aluno.id) &&
          aluno.status === "ativo"
      );
    
      const alunosDisponiveisFiltrados = alunosDisponiveis.filter((aluno) => {
        const termo = buscaDisponivel.toLowerCase().trim();
        if (!termo) return true;
        const cpfTermo = buscaDisponivel.replace(/\D/g, "");
        return (
          (aluno.nome || "").toLowerCase().includes(termo) ||
          (aluno.nome_social || "").toLowerCase().includes(termo) ||
          (cpfTermo.length > 0 && (aluno.cpf || "").replace(/\D/g, "").includes(cpfTermo))
        );
      });
    
      const alunosNaTurmaFiltrados = alunosNaTurma.filter((aluno) => {
        const termo = buscaNaTurma.toLowerCase().trim();
        if (!termo) return true;
        const cpfTermo = buscaNaTurma.replace(/\D/g, "");
        return (
          (aluno.nome || "").toLowerCase().includes(termo) ||
          (aluno.nome_social || "").toLowerCase().includes(termo) ||
          (cpfTermo.length > 0 && (aluno.cpf || "").replace(/\D/g, "").includes(cpfTermo))
        );
      });
    
      return (
        <div className="space-y-4">
          <div>
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-lg font-semibold">
                Alunos Disponíveis ({alunosDisponiveis.length})
              </h3>
            </div>
            <div className="relative mb-2">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Buscar por nome ou CPF..."
                value={buscaDisponivel}
                onChange={(e) => setBuscaDisponivel(e.target.value)}
                className="pl-9"
              />
            </div>
            <div className="max-h-48 overflow-y-auto border rounded p-2 space-y-1">
              {alunosDisponiveisFiltrados.length === 0 ? (
                <p className="text-center text-sm text-gray-400 py-4">
                  {buscaDisponivel ? "Nenhum aluno encontrado" : "Nenhum aluno disponível"}
                </p>
              ) : (
                alunosDisponiveisFiltrados.map((aluno) => (
                  <div
                    key={aluno.id}
                    className="flex justify-between items-center p-2 hover:bg-gray-50 rounded"
                  >
                    <div>
                      <span className="font-medium text-sm">
                        {aluno.nome_social || aluno.nome}
                      </span>
                      {aluno.nome_social && (
                        <span className="text-xs text-gray-400 ml-1">({aluno.nome})</span>
                      )}
                      <span className="text-xs text-gray-500 ml-2">{aluno.cpf}</span>
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => onAdd(aluno.id)}
                      className="text-green-600 hover:text-green-700 hover:bg-green-50"
                    >
                      <Plus className="h-4 w-4 mr-1" />
                      Adicionar
                    </Button>
                  </div>
                ))
              )}
            </div>
          </div>
    
          <div>
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-lg font-semibold">
                Alunos na Turma ({alunosNaTurma.filter(a => a.status === "ativo").length}
                /{selectedTurmaForAlunos?.vagas_total || 0})
              </h3>
            </div>
            <div className="relative mb-2">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Buscar aluno na turma..."
                value={buscaNaTurma}
                onChange={(e) => setBuscaNaTurma(e.target.value)}
                className="pl-9"
              />
            </div>
            <div className="max-h-48 overflow-y-auto border rounded p-2 space-y-1">
              {alunosNaTurmaFiltrados.length === 0 ? (
                <p className="text-center text-sm text-gray-400 py-4">
                  {buscaNaTurma ? "Nenhum aluno encontrado" : "Nenhum aluno na turma ainda"}
                </p>
              ) : (
                alunosNaTurmaFiltrados.map((aluno) => (
                  <div
                    key={aluno.id}
                    className={`flex justify-between items-center p-2 hover:bg-gray-50 rounded ${
                      aluno.status === "desistente" ? "opacity-60 bg-red-50" : ""
                    }`}
                  >
                    <div>
                      <span
                        className={`font-medium text-sm ${
                          aluno.status === "desistente" ? "line-through text-red-600" : ""
                        }`}
                      >
                        {aluno.nome_social || aluno.nome}
                      </span>
                      <span className="text-xs text-gray-500 ml-2">{aluno.cpf}</span>
                      {aluno.status === "desistente" && (
                        <span className="text-xs text-red-600 ml-2 font-semibold">
                          (DESISTENTE)
                        </span>
                      )}
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => onRemove(aluno.id)}
                      className="text-red-600 hover:text-red-700 hover:bg-red-50"
                      disabled={aluno.status === "desistente"}
                    >
                      <Trash2 className="h-4 w-4 mr-1" />
                      Remover
                    </Button>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      );
    };
                          
  // Turmas Manager Component CORRIGIDO
  const TurmasManager = (props) => {
    const { user } = useAuth(); // ✅ CORREÇÃO: Adicionar useAuth para acessar user
    const [turmas, setTurmas] = useState([]);
    const [unidades, setUnidades] = useState([]);
    const [cursos, setCursos] = useState([]);
    const [usuarios, setUsuarios] = useState([]);
    const [alunos, setAlunos] = useState([]);
    const [loading, setLoading] = useState(true);
    const [isDialogOpen, setIsDialogOpen] = useState(false);
    const [isAlunoDialogOpen, setIsAlunoDialogOpen] = useState(false);
    const [editingTurma, setEditingTurma] = useState(null);
    const [selectedTurmaForAlunos, setSelectedTurmaForAlunos] = useState(null);
    const [formData, setFormData] = useState({
      nome: "",
      unidade_id: "",
      curso_id: "",
      instrutor_ids: [], // Array para múltiplos instrutores
      data_inicio: "",
      data_fim: "",
      horario_inicio: "",
      horario_fim: "",
      dias_semana: [],
      vagas_total: 30,
      ciclo: "01/2025",
      tipo_turma: "regular",
    });
  const { toast } = useToast();
    const isMountedRef = React.useRef(true);
    const { filtros, setFiltros } = props; // recebe do Dashboard
    const filtroNome = filtros.nome;
    const filtroTipo = filtros.tipo;
    const filtroUnidade = filtros.unidade;
    const filtroCurso = filtros.curso;
    useEffect(() => {
      isMountedRef.current = true;
      fetchData();
      return () => {
        isMountedRef.current = false;
      };
    }, []);
  
    const fetchData = async () => {
      try {
        console.log("Fetching turmas data...");

    const isAdmin = user?.tipo === "admin";

    const [turmasRes, unidadesRes, cursosRes, alunosRes, instrutoresRes, pedagogosRes] =
      await Promise.all([
        axios.get(`${API}/classes`),
        axios.get(`${API}/units`),
        axios.get(`${API}/courses`),
        axios.get(`${API}/students`),
        axios.get(`${API}/users?tipo=instrutor`).catch(() => ({ data: [] })),
        axios.get(`${API}/users?tipo=pedagogo`).catch(() => ({ data: [] })),
      ]);
  
        // ✅ COMBINAR INSTRUTORES E PEDAGOGOS para seleção de responsável
        // Garantir que os dados sejam arrays
        const instrutores = Array.isArray(instrutoresRes.data)
          ? instrutoresRes.data
          : [];
        const pedagogos = Array.isArray(pedagogosRes.data)
          ? pedagogosRes.data
          : [];
        const todosUsuarios = [
          ...instrutores.map((u) => ({ ...u, tipo_label: "Instrutor" })),
          ...pedagogos.map((u) => ({ ...u, tipo_label: "Pedagogo" })),
        ];
  
        console.log("Turmas:", turmasRes.data);
        console.log("Unidades:", unidadesRes.data);
        console.log("Cursos:", cursosRes.data);
        console.log("Instrutores:", instrutoresRes.data);
        console.log("Pedagogos:", pedagogosRes.data);
        console.log("Todos Usuários:", todosUsuarios);
        console.log("Alunos:", alunosRes.data);
  
        // Garantir que todos os dados sejam arrays e só atualizar se componente ainda estiver montado
        if (isMountedRef.current) {
          const turmasOrdenadas = Array.isArray(turmasRes.data)
            ? turmasRes.data.sort((a, b) => a.nome.localeCompare(b.nome, "pt-BR"))
            : [];
          setTurmas(turmasOrdenadas);
          setUnidades(Array.isArray(unidadesRes.data) ? unidadesRes.data : []);
          setCursos(Array.isArray(cursosRes.data) ? cursosRes.data : []);
          setUsuarios(todosUsuarios); // ✅ Usar lista combinada
          setAlunos(Array.isArray(alunosRes.data) ? alunosRes.data : []);
        }
      } catch (error) {
        console.error("Error fetching data:", error);
        // Garantir que todos os estados sejam arrays vazios em caso de erro
        if (isMountedRef.current) {
          setTurmas([]);
          setUnidades([]);
          setCursos([]);
          setUsuarios([]);
          setAlunos([]);
          toast({
            title: "Erro ao carregar dados",
            description: "Não foi possível carregar os dados necessários",
            variant: "destructive",
          });
        }
      } finally {
        if (isMountedRef.current) {
          setLoading(false);
        }
      }
    };
  
    const handleSubmit = async (e) => {
      e.preventDefault();
      try {
        console.log("📝 Enviando dados da turma:", formData);
  
        // COMPATIBILIDADE: Enviar ambos os formatos até Render atualizar
        const payload = {
          ...formData,
          instrutor_id:
            formData.instrutor_ids && formData.instrutor_ids.length > 0
              ? formData.instrutor_ids[0]
              : null,
        };
  
        if (editingTurma) {
          const response = await axios.put(
            `${API}/classes/${editingTurma.id}`,
            payload,
          );
          console.log("✅ Turma atualizada:", response.data);
          toast({
            title: "Turma atualizada com sucesso!",
            description: "As informações da turma foram atualizadas.",
          });
        } else {
          const response = await axios.post(`${API}/classes`, payload);
          console.log("✅ Turma criada:", response.data);
          toast({
            title: "Turma criada com sucesso!",
            description: "A nova turma foi adicionada ao sistema.",
          });
        }
  
        // Fechar modal primeiro
        setIsDialogOpen(false);
  
        // Aguardar o modal fechar antes de atualizar estados
        setTimeout(() => {
          setEditingTurma(null);
          resetForm();
          fetchData();
        }, 100);
      } catch (error) {
        console.error("❌ Erro ao salvar turma:", error);
        console.error("Detalhes do erro:", error.response?.data);
        toast({
          title: editingTurma ? "Erro ao atualizar turma" : "Erro ao criar turma",
          description:
            error.response?.data?.detail || error.message || "Tente novamente",
          variant: "destructive",
        });
      }
    };
  
    const resetForm = () => {
      // ✅ AUTO-PREENCHIMENTO: Para não-admin, pré-preencher unidade e instrutor
      const defaultUnidadeId =
        user?.tipo !== "admin" ? user?.unidade_id || "" : "";
      const defaultInstrutorIds = user?.tipo !== "admin" ? [user?.id] : [];
      const defaultCursoId = user?.tipo !== "admin" ? user?.curso_id || "" : "";
  
      setFormData({
        nome: "",
        unidade_id: defaultUnidadeId,
        curso_id: defaultCursoId,
        instrutor_ids: defaultInstrutorIds,
        data_inicio: "",
        data_fim: "",
        horario_inicio: "",
        horario_fim: "",
        dias_semana: [],
        vagas_total: 30,
        ciclo: "01/2025",
        tipo_turma: user?.tipo === "pedagogo" ? "extensao" : "regular",
      });
    };
  
    const handleViewTurma = (turma) => {
      const unidadeNome =
        (Array.isArray(unidades) &&
          unidades.find((u) => u.id === turma.unidade_id)?.nome) ||
        "N/A";
      const cursoNome =
        (Array.isArray(cursos) &&
          cursos.find((c) => c.id === turma.curso_id)?.nome) ||
        "N/A";
      const instrutorNome =
        (Array.isArray(usuarios) &&
          usuarios.find((u) => u.id === turma.instrutor_id)?.nome) ||
        "N/A";
  
      alert(
        `📋 DETALHES DA TURMA\n\n` +
          `Nome: ${turma.nome}\n` +
          `Unidade: ${unidadeNome}\n` +
          `Curso: ${cursoNome}\n` +
          `Instrutor: ${instrutorNome}\n` +
          `Período: ${new Date(turma.data_inicio + "T00:00:00").toLocaleDateString("pt-BR")} a ${new Date(turma.data_fim + "T00:00:00").toLocaleDateString("pt-BR")}\n` +
          `Horário: ${turma.horario_inicio} às ${turma.horario_fim}\n` +
          `Vagas: ${turma.vagas_ocupadas || 0}/${turma.vagas_total}\n` +
          `Ciclo: ${turma.ciclo}\n` +
          `Status: ${turma.ativo ? "Ativa" : "Inativa"}`,
      );
    };
  
    const handleEdit = (turma) => {
      if (isMountedRef.current) {
        console.log("🔧 Editando turma:", turma);
        console.log("📋 instrutor_ids da turma:", turma.instrutor_ids);
        setEditingTurma(turma);
        setFormData({
          nome: turma.nome,
          unidade_id: turma.unidade_id,
          curso_id: turma.curso_id,
          instrutor_ids: turma.instrutor_ids || [], // Array de instrutores
          data_inicio: turma.data_inicio,
          data_fim: turma.data_fim,
          horario_inicio: turma.horario_inicio,
          horario_fim: turma.horario_fim,
          dias_semana: turma.dias_semana || [],
          vagas_total: turma.vagas_total,
          ciclo: turma.ciclo,
          tipo_turma: turma.tipo_turma || "regular",
        });
        console.log("✅ FormData após edição:", {
          instrutor_ids: turma.instrutor_ids || [],
        });
        setIsDialogOpen(true);
      }
    };
  
    const handleOpenDialog = () => {
      if (isMountedRef.current) {
        setEditingTurma(null);
        resetForm();
        setIsDialogOpen(true);
      }
    };
  
    const handleManageAlunos = (turma) => {
      if (isMountedRef.current) {
        setSelectedTurmaForAlunos(turma);
        setIsAlunoDialogOpen(true);
      }
    };
  
    const handleDeleteTurma = async (turma) => {
      // 🔒 VERIFICAÇÃO: Apenas admin pode deletar
      if (user?.tipo !== "admin") {
        toast({
          title: "Acesso negado",
          description: "Apenas administradores podem deletar turmas",
          variant: "destructive",
        });
        return;
      }
  
      // ⚠️ CONFIRMAÇÃO: Pedir confirmação antes de deletar
      const confirmar = window.confirm(
        `⚠️ ATENÇÃO: Tem certeza que deseja DELETAR a turma "${turma.nome}"?\n\n` +
          `Esta ação é IRREVERSÍVEL e:\n` +
          `• Removerá permanentemente a turma do sistema\n` +
          `• Não afetará os alunos (eles continuarão cadastrados)\n` +
          `• Não poderá ser desfeita\n\n` +
          `Digite "SIM" para confirmar:`,
      );
  
      if (!confirmar) {
        return;
      }
  
      try {
        const response = await axios.delete(`${API}/classes/${turma.id}`);
  
        toast({
          title: "Turma deletada com sucesso!",
          description: `A turma "${turma.nome}" foi removida permanentemente`,
          className: "bg-green-50 border-green-200",
        });
  
        // Atualizar lista de turmas
        fetchData();
  
        console.log("🗑️ Turma deletada:", response.data);
      } catch (error) {
        console.error("❌ Erro ao deletar turma:", error);
  
        // Tratar erros específicos do backend
        if (error.response?.status === 400) {
          toast({
            title: "Não é possível deletar",
            description:
              error.response.data.detail || "Turma possui dependências",
            variant: "destructive",
          });
        } else if (error.response?.status === 403) {
          toast({
            title: "Acesso negado",
            description: "Apenas administradores podem deletar turmas",
            variant: "destructive",
          });
        } else {
          toast({
            title: "Erro ao deletar turma",
            description: "Ocorreu um erro interno. Tente novamente.",
            variant: "destructive",
          });
        }
      }
    };
      
    const handleAddAlunoToTurma = async (alunoId) => {
      try {
        await axios.put(
          `${API}/classes/${selectedTurmaForAlunos.id}/students/${alunoId}`,
        );
        toast({
          title: "Aluno adicionado com sucesso!",
          description: "O aluno foi adicionado à turma.",
        });
        // Atualizar selectedTurmaForAlunos imediatamente para refletir a mudança
        setSelectedTurmaForAlunos((prev) => ({
          ...prev,
          alunos_ids: [...(prev.alunos_ids || []), alunoId],
        }));
        fetchData();
      } catch (error) {
        toast({
          title: "Erro ao adicionar aluno",
          description: error.response?.data?.detail || "Tente novamente",
          variant: "destructive",
        });
      }
    };
    
    const handleRemoveAlunoFromTurma = async (alunoId) => {
      try {
        await axios.delete(
          `${API}/classes/${selectedTurmaForAlunos.id}/students/${alunoId}`,
        );
        toast({
          title: "Aluno removido com sucesso!",
          description: "O aluno foi removido da turma.",
        });
        // Atualizar selectedTurmaForAlunos imediatamente para refletir a mudança
        setSelectedTurmaForAlunos((prev) => ({
          ...prev,
          alunos_ids: (prev.alunos_ids || []).filter((id) => id !== alunoId),
        }));
        fetchData();
      } catch (error) {
        toast({
          title: "Erro ao remover aluno",
          description: error.response?.data?.detail || "Tente novamente",
          variant: "destructive",
        });
      }
    };  
    const turmasFiltradas = turmas.filter((turma) => {
      const nomeOk = turma.nome.toLowerCase().includes(filtroNome.toLowerCase());
      const tipoOk = filtroTipo === "todos" || turma.tipo_turma === filtroTipo;
      const unidadeOk = filtroUnidade === "todos" || turma.unidade_id === filtroUnidade;
      const cursoOk = filtroCurso === "todos" || turma.curso_id === filtroCurso;
      return nomeOk && tipoOk && unidadeOk && cursoOk;
    });
    
    if (loading)
      return (
        
        <div key="turmas-loading" className="p-8 text-center">
          Carregando turmas...
        </div>
      );
    if (!isMountedRef.current) return null;
  
    return (
      <Card key="turmas-content">
        <CardHeader>
          <div className="flex justify-between items-center">
            <div>
              <CardTitle>Gerenciamento de Turmas</CardTitle>
              <CardDescription>
                Visualize e gerencie todas as turmas do sistema
              </CardDescription>
            </div>
            <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
              <DialogTrigger asChild>
                <Button
                  onClick={handleOpenDialog}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Nova Turma
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
                <DialogHeader>
                  <DialogTitle>
                    {editingTurma ? "Editar Turma" : "Criar Nova Turma"}
                  </DialogTitle>
                  <DialogDescription>
                    {editingTurma
                      ? "Atualize os dados da turma"
                      : "Preencha os dados para criar uma nova turma"}
                  </DialogDescription>
                </DialogHeader>
                <form onSubmit={handleSubmit} className="space-y-4 pb-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="nome">Nome da Turma</Label>
                      <Input
                        id="nome"
                        value={formData.nome}
                        onChange={(e) =>
                          setFormData({ ...formData, nome: e.target.value })
                        }
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="ciclo">Ciclo</Label>
                      <Input
                        id="ciclo"
                        value={formData.ciclo}
                        onChange={(e) =>
                          setFormData({ ...formData, ciclo: e.target.value })
                        }
                        placeholder="01/2025"
                        required
                      />
                    </div>
                  </div>
  
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label>
                        Unidade{" "}
                        {user?.tipo === "admin"
                          ? `(${unidades.length} disponíveis)`
                          : "(Sua unidade)"}
                      </Label>
                      {user?.tipo === "admin" ? (
                        <Select
                          value={formData.unidade_id}
                          onValueChange={(value) =>
                            setFormData({ ...formData, unidade_id: value })
                          }
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="Selecione a unidade" />
                          </SelectTrigger>
                          <SelectContent>
                            {Array.isArray(unidades) &&
                              unidades.map((unidade) => (
                                <SelectItem key={unidade.id} value={unidade.id}>
                                  {unidade.nome}
                                </SelectItem>
                              ))}
                          </SelectContent>
                        </Select>
                      ) : (
                        <Input
                          value={
                            (Array.isArray(unidades) &&
                              unidades.find((u) => u.id === formData.unidade_id)
                                ?.nome) ||
                            user?.unidade_nome ||
                            "Sua unidade"
                          }
                          readOnly
                          className="bg-gray-50 cursor-not-allowed"
                        />
                      )}
                    </div>
  
                    <div className="space-y-2">
                      <Label>
                        Curso{" "}
                        {user?.tipo === "admin"
                          ? `(${cursos.length} disponíveis)`
                          : "(Seu curso)"}
                      </Label>
                      {user?.tipo === "admin" ? (
                        <Select
                          value={formData.curso_id}
                          onValueChange={(value) =>
                            setFormData({ ...formData, curso_id: value })
                          }
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="Selecione o curso" />
                          </SelectTrigger>
                          <SelectContent>
                            {Array.isArray(cursos) &&
                              cursos.map((curso) => (
                                <SelectItem key={curso.id} value={curso.id}>
                                  {curso.nome}
                                </SelectItem>
                              ))}
                          </SelectContent>
                        </Select>
                      ) : (
                        <Input
                          value={
                            (Array.isArray(cursos) &&
                              cursos.find((c) => c.id === formData.curso_id)
                                ?.nome) ||
                            user?.curso_nome ||
                            "Seu curso"
                          }
                          readOnly
                          className="bg-gray-50 cursor-not-allowed"
                        />
                      )}
                    </div>
                  </div>
  
                  <div className="space-y-2">
                    <Label>
                      Responsáveis (até 2){" "}
                      {user?.tipo === "admin"
                        ? `(${usuarios.length} instrutores/pedagogos disponíveis)`
                        : "(Você)"}
                    </Label>
                    {user?.tipo === "admin" ? (
                      <div className="space-y-2">
                        {/* Primeiro Instrutor */}
                        <Select
                          value={formData.instrutor_ids[0] || ""}
                          onValueChange={(value) => {
                            const newIds = [...formData.instrutor_ids];
                            newIds[0] = value;
                            setFormData({
                              ...formData,
                              instrutor_ids: newIds.filter((id) => id),
                            });
                          }}
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="Selecione o 1º responsável" />
                          </SelectTrigger>
                          <SelectContent>
                            {Array.isArray(usuarios) &&
                              usuarios.map((usuario) => (
                                <SelectItem key={usuario.id} value={usuario.id}>
                                  {usuario.nome} ({usuario.tipo_label})
                                </SelectItem>
                              ))}
                          </SelectContent>
                        </Select>
  
                        {/* Segundo Instrutor (Opcional) */}
                        <div className="flex gap-2">
                          <Select
                            value={formData.instrutor_ids[1] || "none"}
                            onValueChange={(value) => {
                              const newIds = [...formData.instrutor_ids];
                              if (value && value !== "none") {
                                newIds[1] = value;
                                setFormData({
                                  ...formData,
                                  instrutor_ids: newIds,
                                });
                              } else {
                                // Remover segundo instrutor
                                newIds.splice(1, 1);
                                setFormData({
                                  ...formData,
                                  instrutor_ids: newIds,
                                });
                              }
                            }}
                          >
                            <SelectTrigger>
                              <SelectValue placeholder="Selecione o 2º responsável (opcional)" />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="none">Nenhum</SelectItem>
                              {Array.isArray(usuarios) &&
                                usuarios
                                  .filter(
                                    (u) => u.id !== formData.instrutor_ids[0],
                                  )
                                  .map((usuario) => (
                                    <SelectItem
                                      key={usuario.id}
                                      value={usuario.id}
                                    >
                                      {usuario.nome} ({usuario.tipo_label})
                                    </SelectItem>
                                  ))}
                            </SelectContent>
                          </Select>
                          {formData.instrutor_ids[1] && (
                            <button
                              type="button"
                              onClick={() => {
                                const newIds = [...formData.instrutor_ids];
                                newIds.splice(1, 1);
                                setFormData({
                                  ...formData,
                                  instrutor_ids: newIds,
                                });
                              }}
                              className="px-3 py-2 text-sm text-red-600 hover:bg-red-50 rounded-md"
                              title="Remover 2º instrutor"
                            >
                              ✕
                            </button>
                          )}
                        </div>
                      </div>
                    ) : (
                      <Input
                        value={user?.nome || "Você"}
                        readOnly
                        className="bg-gray-50 cursor-not-allowed"
                      />
                    )}
                  </div>
  
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="data_inicio">Data Início</Label>
                      <Input
                        id="data_inicio"
                        type="date"
                        value={formData.data_inicio}
                        onChange={(e) =>
                          setFormData({
                            ...formData,
                            data_inicio: e.target.value,
                          })
                        }
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="data_fim">Data Fim</Label>
                      <Input
                        id="data_fim"
                        type="date"
                        value={formData.data_fim}
                        onChange={(e) =>
                          setFormData({ ...formData, data_fim: e.target.value })
                        }
                        required
                      />
                    </div>
                  </div>
  
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="horario_inicio">Horário Início</Label>
                      <Input
                        id="horario_inicio"
                        type="time"
                        value={formData.horario_inicio}
                        onChange={(e) =>
                          setFormData({
                            ...formData,
                            horario_inicio: e.target.value,
                          })
                        }
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="horario_fim">Horário Fim</Label>
                      <Input
                        id="horario_fim"
                        type="time"
                        value={formData.horario_fim}
                        onChange={(e) =>
                          setFormData({
                            ...formData,
                            horario_fim: e.target.value,
                          })
                        }
                        required
                      />
                    </div>
                  </div>
  
                  {/* Campo Tipo de Turma */}
                  <div className="space-y-2">
                    <Label>Tipo de Turma</Label>
                    <Select
                      value={formData.tipo_turma}
                      onValueChange={(value) =>
                        setFormData({ ...formData, tipo_turma: value })
                      }
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Selecione o tipo" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="regular">
                          Regular (Curso Técnico)
                        </SelectItem>
                        <SelectItem value="extensao">
                          Extensão (Curso Livre)
                        </SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
  
                  <div className="space-y-2">
                    <Label htmlFor="vagas_total">Vagas Total</Label>
                    <Input
                      id="vagas_total"
                      type="number"
                      value={formData.vagas_total}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          vagas_total: parseInt(e.target.value),
                        })
                      }
                      min="1"
                      required
                    />
                  </div>
  
                  <Button
                    type="submit"
                    className="w-full bg-blue-600 hover:bg-blue-700"
                  >
                    <Save className="h-4 w-4 mr-2" />
                    {editingTurma ? "Atualizar Turma" : "Criar Turma"}
                  </Button>
                </form>
              </DialogContent>
            </Dialog>
          </div>
        </CardHeader>
        <CardContent>
                      {/* 🔍 FILTROS DE TURMAS */}
          <div className="mb-4 p-4 bg-gray-50 border rounded-lg">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
              <div className="space-y-1">
                <Label className="text-sm">Buscar por nome</Label><Input placeholder="Nome da turma..." value={filtroNome} onChange={(e) => setFiltros({ ...filtros, nome: e.target.value })} />              </div>
              <div className="space-y-1">
                <Label className="text-sm">Tipo</Label>
                <Select value={filtroTipo} onValueChange={(v) => setFiltros({ ...filtros, tipo: v })}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="todos">Todos</SelectItem>
                    <SelectItem value="regular">Regular</SelectItem>
                    <SelectItem value="extensao">Extensão</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-1">
                <Label className="text-sm">Unidade</Label>
                <Select value={filtroUnidade} onValueChange={(v) => setFiltros({ ...filtros, unidade: v })}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="todos">Todas</SelectItem>
                    {Array.isArray(unidades) && unidades.map((u) => (
                      <SelectItem key={u.id} value={u.id}>{u.nome}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-1">
                <Label className="text-sm">Curso</Label>
                <Select value={filtroCurso} onValueChange={(v) => setFiltros({ ...filtros, curso: v })}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="todos">Todos</SelectItem>
                    {Array.isArray(cursos) && cursos.map((c) => (
                      <SelectItem key={c.id} value={c.id}>{c.nome}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <Button variant="outline" size="sm" className="mt-3" onClick={() => setFiltros({ nome: "", tipo: "todos", unidade: "todos", curso: "todos" })}>           <X className="h-4 w-4 mr-1" /> Limpar Filtros
            </Button>
          </div>
          <div className="table-container">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Nome</TableHead>
                  <TableHead>Tipo</TableHead>
                  <TableHead>Ciclo</TableHead>
                  <TableHead>Período</TableHead>
                  <TableHead>Horário</TableHead>
                  <TableHead>Vagas</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Ações</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {Array.isArray(turmasFiltradas) &&
                  turmasFiltradas.map((turma) => (
                    <TableRow key={turma.id}>
                      <TableCell className="font-medium">{turma.nome}</TableCell>
                      <TableCell>
                        <Badge
                          variant={
                            turma.tipo_turma === "extensao"
                              ? "destructive"
                              : "default"
                          }
                        >
                          {turma.tipo_turma === "extensao"
                            ? "Extensão"
                            : "Regular"}
                        </Badge>
                      </TableCell>
                      <TableCell>{turma.ciclo}</TableCell>
                      <TableCell>
                        {new Date(turma.data_inicio + "T00:00:00").toLocaleDateString("pt-BR")} -{" "}
                        {new Date(turma.data_fim + "T00:00:00").toLocaleDateString("pt-BR")}
                      </TableCell>
                      <TableCell>
                        {turma.horario_inicio} - {turma.horario_fim}
                      </TableCell>
                      <TableCell>
                      {(turma.alunos_ids?.length ?? turma.vagas_ocupadas ?? 0)}/{turma.vagas_total}
                    </TableCell>
                      <TableCell>
                        <Badge variant={turma.ativo ? "default" : "secondary"}>
                          {turma.ativo ? "Ativa" : "Inativa"}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex space-x-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleViewTurma(turma)}
                            title="Visualizar detalhes"
                          >
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleManageAlunos(turma)}
                            title="Gerenciar alunos"
                            className="text-green-600 hover:text-green-700"
                          >
                            <UserPlus className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleEdit(turma)}
                            title="Editar turma"
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          {/* 🗑️ BOTÃO DELETAR TURMA - Apenas para Admin */}
                          {user?.tipo === "admin" && (
                            <Button
                              variant="destructive"
                              size="sm"
                              onClick={() => handleDeleteTurma(turma)}
                              title="Deletar turma"
                              className="text-red-600 hover:text-red-700 border-red-300 hover:bg-red-50"
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          )}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
              </TableBody>
            </Table>
          </div></CardContent>

          <Dialog open={isAlunoDialogOpen} onOpenChange={setIsAlunoDialogOpen}>
            <DialogContent className="max-w-4xl">
              <DialogHeader>
                <DialogTitle>
                  Gerenciar Alunos - {selectedTurmaForAlunos?.nome}
                </DialogTitle>
                <DialogDescription>
                  Adicione ou remova alunos desta turma
                </DialogDescription>
              </DialogHeader>
              <AlunosTurmaManager
                selectedTurmaForAlunos={selectedTurmaForAlunos}
                alunos={alunos}
                onAdd={handleAddAlunoToTurma}
                onRemove={handleRemoveAlunoFromTurma}
              />
            </DialogContent>
          </Dialog>
          </Card>
            );
          };

                      
  // 📊 RELATÓRIOS DINÂMICOS - Atualizados Automaticamente
  const RelatoriosManager = () => {
    const { user } = useAuth();
    const { toast } = useToast();
    const [stats, setStats] = useState({});
    const [loading, setLoading] = useState(true);
  
    // � DADOS ESSENCIAIS PARA CÁLCULOS FASE 3
    const [alunos, setAlunos] = useState(() => {
      try {
        const cached = localStorage.getItem("ios_alunos_cache");
        return cached ? JSON.parse(cached) : [];
      } catch {
        return [];
      }
    });
  
    const [chamadas, setChamadas] = useState(() => {
      try {
        const cached = localStorage.getItem("ios_chamadas_cache");
        return cached ? JSON.parse(cached) : [];
      } catch {
        return [];
      }
    });
  
    // 📊 STATUS DE CONEXÃO COM MONGODB
    const [dadosCarregando, setDadosCarregando] = useState(true);
    const [ultimaAtualizacao, setUltimaAtualizacao] = useState(() => {
      return localStorage.getItem("ios_ultima_atualizacao") || null;
    });
  
    // �🔧 HEALTH CHECK - FASE 5
    const [healthStatus, setHealthStatus] = useState(null);
    const [showHealthCheck, setShowHealthCheck] = useState(false);
  
    // 🔍 FILTROS AVANÇADOS PARA ADMIN
    const [filtros, setFiltros] = useState({
      data_inicio: "",
      data_fim: "",
      unidade_id: "all",
      curso_id: "all",
      turma_id: "all",
    });
    const [showFilters, setShowFilters] = useState(false);
  
    // Estados para os dropdowns dos filtros
    const [unidades, setUnidades] = useState([]);
    const [cursos, setCursos] = useState([]);
    const [turmas, setTurmas] = useState([]);
  
            useEffect(() => {
              fetchDadosBasicos();
            }, []);
            useEffect(() => {
      if (user?.tipo === "admin" || user?.tipo === "gestor") {
        fetchFilterData();
      }
      const interval = setInterval(() => fetchDynamicStats(filtros), 30000);
      return () => clearInterval(interval);
    }, [user]);
    
    useEffect(() => {
      const timer = setTimeout(() => fetchDynamicStats(filtros), 500);
      return () => clearTimeout(timer);
    }, [filtros]);
  
    // 🔍 FUNÇÃO PING PARA ACORDAR RENDER (DASHBOARD)
    const wakeUpBackendDashboard = async () => {
      console.log("🔔 Acordando backend Render para dashboard...");
      try {
        const pingResponse = await axios.get(`${API}/ping`, { timeout: 30000 });
        console.log("✅ Backend acordado para dashboard:", pingResponse.data);
        return true;
      } catch (error) {
        console.error("❌ Erro ao acordar backend:", error);
        return false;
      }
    };

const fetchDadosBasicos = async () => {
    console.log("🔍 Iniciando carregamento direto MongoDB via Render Backend");
    setDadosCarregando(true);

    try {
      // 🚀 PRIMEIRO: Acordar o backend
      const backendAwake = await wakeUpBackendDashboard();
      if (!backendAwake) {
        console.warn(
          "⚠️ Backend pode estar dormindo, tentando requisições diretas...",
        );
      }

      // 🎯 BUSCAR APENAS ALUNOS — chamadas são calculadas pelo backend em /reports/teacher-stats
      const alunosResponse = await axios.get(`${API}/students`, {
        timeout: 60000,
        headers: {
          Accept: "application/json",
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
      });

      // ✅ DEFINIR DADOS SEMPRE (nunca undefined)
      const alunosData = Array.isArray(alunosResponse.data)
        ? alunosResponse.data
        : [];

      setAlunos(alunosData);
      setChamadas([]); // Chamadas são calculadas pelo backend, não precisamos aqui

      console.log(`✅ Dados carregados: ${alunosData.length} alunos`);

      toast({
        title: "✅ Dados Carregados",
        description: `${alunosData.length} alunos carregados com sucesso`,
        variant: "default",
      });
    } catch (error) {
      console.error("❌ Erro ao carregar dados:", error);

      if (error.response?.status === 401) {
        console.error("🚨 Erro 401: Token inválido ou expirado - faça login novamente");
      } else if (error.code === "ECONNABORTED") {
        console.error("🚨 Timeout: Backend demorou mais que 60s");
      }

      // ⚠️ SEMPRE DEFINIR ARRAYS VAZIOS (nunca undefined)
      setAlunos([]);
      setChamadas([]);

      toast({
        title: "❌ Erro ao Carregar Dados",
        description: "Falha na conexão. Verifique se o backend está online.",
        variant: "destructive",
      });
    } finally {
      setDadosCarregando(false);
      setUltimaAtualizacao(new Date().toISOString());
    }
  };
                      
    const fetchFilterData = async () => {
      try {
        const [unidadesRes, cursosRes, turmasRes] = await Promise.all([
          axios.get(`${API}/units`),
          axios.get(`${API}/courses`),
          axios.get(`${API}/classes`),
        ]);
  
        setUnidades(unidadesRes.data);
        setCursos(cursosRes.data);
        setTurmas(turmasRes.data);
      } catch (error) {
        console.error("Erro ao carregar dados dos filtros:", error);
      }
    };
  
    const fetchDynamicStats = async (customFilters = null) => {
      try {
        // 🎯 FILTROS: Aplicar filtros se for admin e filtros estiverem definidos
        let url = `${API}/reports/teacher-stats`;
        const filtersToUse = customFilters || filtros;
  
        if (
          (user?.tipo === "admin" || user?.tipo === "gestor") &&
          (filtersToUse.data_inicio ||
            filtersToUse.data_fim ||
            (filtersToUse.unidade_id && filtersToUse.unidade_id !== "all") ||
            (filtersToUse.curso_id && filtersToUse.curso_id !== "all") ||
            (filtersToUse.turma_id && filtersToUse.turma_id !== "all"))
        ) {
          const params = new URLSearchParams();
          if (filtersToUse.data_inicio)
            params.append("data_inicio", filtersToUse.data_inicio);
          if (filtersToUse.data_fim)
            params.append("data_fim", filtersToUse.data_fim);
          if (filtersToUse.unidade_id && filtersToUse.unidade_id !== "all")
            params.append("unidade_id", filtersToUse.unidade_id);
          if (filtersToUse.curso_id && filtersToUse.curso_id !== "all")
            params.append("curso_id", filtersToUse.curso_id);
          if (filtersToUse.turma_id && filtersToUse.turma_id !== "all")
            params.append("turma_id", filtersToUse.turma_id);
          url += `?${params.toString()}`;
        }
  
        const response = await axios.get(url);
  
        // 📊 FASE 3: Aplicar regras de negócio precisas
        if (alunos && alunos.length > 0) {
          const estatisticasLocais = calcularEstatisticasPrecisas(
            alunos,
            chamadas || [],
          );
  
          // 🎯 USAR APENAS DADOS DO BACKEND para consistência
          const statsComPrecisao = {
            ...response.data,
            // Manter alguns cálculos locais apenas para detalhes específicos
            detalhes_por_aluno: estatisticasLocais.estatisticasPorAluno,
            regras_aplicadas: REGRAS_PRESENCA,
            calculo_preciso: true,
            // Usar contagens do backend (fonte única de verdade)
            total_alunos:
              response.data.total_alunos ||
              response.data.alunos_ativos + response.data.alunos_desistentes,
            alunos_ativos: response.data.alunos_ativos,
            desistentes: response.data.alunos_desistentes,
          };
  
          setStats(statsComPrecisao);
          console.log("✅ Estatísticas Fase 3 aplicadas:", {
            taxa: estatisticasLocais.taxaMediaPresenca,
            risco: estatisticasLocais.alunosEmRisco,
            total: estatisticasLocais.totalAlunos,
          });
        } else {
          setStats(response.data);
        }
      } catch (error) {
        console.error("Error fetching dynamic stats:", error);
  
        // 🔄 Fallback com cálculos locais precisos
        if (alunos && alunos.length > 0) {
          console.log("🎯 Aplicando Fase 3 offline - cálculos precisos locais");
          const estatisticasLocais = calcularEstatisticasPrecisas(
            alunos,
            chamadas || [],
          );
  
          setStats({
            taxa_media_presenca: estatisticasLocais.taxaMediaPresenca,
            total_alunos: alunos.length, // Total de todos os alunos
            alunos_ativos: alunos.filter((a) => a.status === "ativo").length,
            alunos_desistentes: alunos.filter((a) => a.status === "desistente")
              .length,
            alunos_em_risco: estatisticasLocais.alunosEmRisco,
            desistentes: alunos.filter((a) => a.status === "desistente").length, // Consistência
            detalhes_por_aluno: estatisticasLocais.estatisticasPorAluno,
            regras_aplicadas: REGRAS_PRESENCA,
            modo_offline: true,
            calculo_preciso: true,
          });
        } else if (user?.tipo === "instrutor") {
          try {
            const fallbackResponse = await axios.get(`${API}/teacher/stats`);
            setStats(fallbackResponse.data);
          } catch (fallbackError) {
            console.error("Fallback also failed:", fallbackError);
          }
        }
      } finally {
        setLoading(false);
      }
    };
  
    // 📊 FASE 4: CSV Export Aprimorado com Dados Precisos
              const downloadFrequencyReport = async () => {
          try {
            toast({
              title: "⏳ Gerando relatório...",
              description: "Buscando dados reais do banco de dados.",
            });
        
            const params = new URLSearchParams({ export_csv: "true" });
        
            if (user?.tipo === "admin" || user?.tipo === "gestor") {
              if (filtros.data_inicio) params.append("data_inicio", filtros.data_inicio);
              if (filtros.data_fim)    params.append("data_fim",    filtros.data_fim);
              if (filtros.unidade_id && filtros.unidade_id !== "all")
                params.append("unidade_id", filtros.unidade_id);
              if (filtros.curso_id && filtros.curso_id !== "all")
                params.append("curso_id", filtros.curso_id);
              if (filtros.turma_id && filtros.turma_id !== "all")
                params.append("turma_id", filtros.turma_id);
            }
        
            const response = await axios.get(
              `${API}/reports/student-frequency?${params.toString()}`,
              { timeout: 120000 }
            );
        
            const csvData = response.data?.csv_data;
        
            if (!csvData || csvData.trim().length === 0) {
              toast({
                title: "⚠️ Sem dados para exportar",
                description: "Nenhuma chamada registrada ainda. Realize chamadas primeiro.",
                variant: "destructive",
              });
              return;
            }
        
            const blob = new Blob(["\ufeff" + csvData], { type: "text/csv;charset=utf-8;" });
            const link = document.createElement("a");
            const objectUrl = URL.createObjectURL(blob);
        
            let fileName = `relatorio_frequencia_${new Date().toISOString().split("T")[0]}`;
            if (filtros.data_inicio && filtros.data_fim)
              fileName += `_${filtros.data_inicio}_a_${filtros.data_fim}`;
            if (filtros.curso_id && filtros.curso_id !== "all")
              fileName += "_CURSO-FILTRADO";
            if (filtros.unidade_id && filtros.unidade_id !== "all")
              fileName += "_UNIDADE-FILTRADA";
            fileName += ".csv";
        
            link.setAttribute("href", objectUrl);
            link.setAttribute("download", fileName);
            link.style.visibility = "hidden";
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(objectUrl);
        
            toast({
              title: "✅ Relatório exportado!",
              description: "Presenças, faltas, unidade e curso incluídos corretamente.",
            });
        
          } catch (error) {
            console.error("Erro ao exportar:", error);
            toast({
              title: "❌ Erro ao exportar",
              description: error.response?.data?.detail || "Verifique sua conexão e tente novamente.",
              variant: "destructive",
            });
          }
        };
    
    // 🔧 EXECUTAR HEALTH CHECK - FASE 5
    const executarHealthCheck = async () => {
      try {
        setLoading(true);
        toast({
          title: "🔍 Executando Health Check",
          description: "Verificando status do sistema Fase 5...",
        });
  
        const healthResult = await verificarHealthSistema(alunos, chamadas);
        setHealthStatus(healthResult);
        setShowHealthCheck(true);
  
        const statusIcon =
          healthResult.status_geral === "saudavel"
            ? "✅"
            : healthResult.status_geral === "alerta"
              ? "⚠️"
              : "❌";
  
        toast({
          title: `${statusIcon} Health Check Concluído`,
          description: `Sistema: ${healthResult.status_geral.toUpperCase()} | ${
            healthResult.fases_ativas.length
          } fases ativas`,
          variant:
            healthResult.status_geral === "erro" ? "destructive" : "default",
        });
      } catch (error) {
        toast({
          title: "❌ Erro no Health Check",
          description: "Falha ao verificar status do sistema",
          variant: "destructive",
        });
      } finally {
        setLoading(false);
      }
    };
  
    // 🧹 Função para limpar filtros
    const limparFiltros = () => {
      const filtrosVazios = {
        data_inicio: "",
        data_fim: "",
        unidade_id: "all",
        curso_id: "all",
        turma_id: "all",
      };
      setFiltros(filtrosVazios);
      setLoading(true);
      fetchDynamicStats(filtrosVazios);
    };
  
    if (loading) {
      return (
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-center">
              <RefreshCw className="h-5 w-5 animate-spin mr-2" />
              <span>Carregando relatórios dinâmicos...</span>
            </div>
          </CardContent>
        </Card>
      );
    }
  
    // 📊 RELATÓRIOS DINÂMICOS - Interface completamente atualizada
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center">
              <BarChart3 className="h-5 w-5 mr-2" />
              {user?.tipo === "admin"
                ? "Relatórios Gerais"
                : "Estatísticas das Minhas Turmas"}
            </div>
            <div className="flex items-center gap-2">{(user?.tipo === "admin" || user?.tipo === "gestor") && (
              <Button
                onClick={() => setShowFilters(!showFilters)}
                  variant="outline"
                  size="sm"
                  className="text-orange-600 border-orange-600 hover:bg-orange-50"
                >
                  <Filter className="h-4 w-4 mr-1" />
                  Filtros
                </Button>
              )}
              <Button
                onClick={downloadFrequencyReport}
                variant="outline"
                size="sm"
                className="text-blue-600 border-blue-600 hover:bg-blue-50 relative"
                title="CSV com dados precisos da Fase 4"
              >
                <Download className="h-4 w-4 mr-1" />
                Exportar CSV
                {stats.calculo_preciso && (
                  <div
                    className="absolute -top-1 -right-1 w-3 h-3 bg-green-500 rounded-full border-2 border-white"
                    title="Dados Fase 4 - Cálculos Precisos"
                  ></div>
                )}
              </Button>
  
              <div className="flex items-center text-sm text-gray-500">
                <RefreshCw className="h-4 w-4 mr-1 animate-spin" />
                Atualizado automaticamente
              </div>
            </div>
          </CardTitle>
          <CardDescription>
            {user?.tipo === "admin"
              ? "Visualize relatórios completos com filtros avançados - Dados em tempo real"
              : "Visualize índices de presença e faltas dos seus alunos - Dados em tempo real"}
          </CardDescription>
        </CardHeader>
  
        {/* 🔍 FILTROS AVANÇADOS PARA ADMIN */}
        {(user?.tipo === "admin" || user?.tipo === "gestor") && showFilters && (
          <div className="mx-6 mb-4 p-4 bg-gray-50 border rounded-lg">
            <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
              <div className="space-y-2">
                <Label className="text-sm font-medium">Data Início</Label>
                <Input
                  type="date"
                  value={filtros.data_inicio}
                  onChange={(e) =>
                    setFiltros({ ...filtros, data_inicio: e.target.value })
                  }
                  className="h-8"
                />
              </div>
              <div className="space-y-2">
                <Label className="text-sm font-medium">Data Fim</Label>
                <Input
                  type="date"
                  value={filtros.data_fim}
                  onChange={(e) =>
                    setFiltros({ ...filtros, data_fim: e.target.value })
                  }
                  className="h-8"
                />
              </div>
              <div className="space-y-2">
                <Label className="text-sm font-medium">Unidade</Label>
                <Select
                  value={filtros.unidade_id || "all"}
                  onValueChange={(value) =>
                    setFiltros({
                      ...filtros,
                      unidade_id: value === "all" ? "" : value,
                    })
                  }
                >
                  <SelectTrigger className="h-8">
                    <SelectValue placeholder="Todas" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Todas as Unidades</SelectItem>
                    {Array.isArray(unidades) &&
                      unidades.map((unidade) => (
                        <SelectItem key={unidade.id} value={unidade.id}>
                          {unidade.nome}
                        </SelectItem>
                      ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label className="text-sm font-medium">Curso</Label>
                <Select
                  value={filtros.curso_id || "all"}
                  onValueChange={(value) =>
                    setFiltros({
                      ...filtros,
                      curso_id: value === "all" ? "" : value,
                    })
                  }
                >
                  <SelectTrigger className="h-8">
                    <SelectValue placeholder="Todos" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Todos os Cursos</SelectItem>
                    {Array.isArray(cursos) &&
                      cursos.map((curso) => (
                        <SelectItem key={curso.id} value={curso.id}>
                          {curso.nome}
                        </SelectItem>
                      ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label className="text-sm font-medium">Turma</Label>
                <Select
                  value={filtros.turma_id || "all"}
                  onValueChange={(value) =>
                    setFiltros({
                      ...filtros,
                      turma_id: value === "all" ? "" : value,
                    })
                  }
                >
                  <SelectTrigger className="h-8">
                    <SelectValue placeholder="Todas" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Todas as Turmas</SelectItem>
                    {Array.isArray(turmas) &&
                      turmas.map((turma) => (
                        <SelectItem key={turma.id} value={turma.id}>
                          {turma.nome}
                        </SelectItem>
                      ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
              <div className="flex gap-2 mt-4">

              <Button onClick={limparFiltros} variant="outline" size="sm">
                <X className="h-4 w-4 mr-1" />
                Limpar
              </Button>
            </div>
          </div>
        )}
        <CardContent>
          {/* Verificar se há dados após filtros */}
            {stats && stats.total_alunos === 0 && !loading && alunos.length === 0 && user?.tipo === "admin" && (
            <div className="text-center py-8">
              <AlertCircle className="h-12 w-12 mx-auto mb-4 text-gray-400" />
              <h3 className="text-lg font-medium text-gray-600 mb-2">
                Nenhum dado encontrado
              </h3>
              <p className="text-gray-500 mb-4">
                Os filtros aplicados não retornaram nenhum resultado. Tente
                ajustar os critérios ou limpar os filtros.
              </p>
              <Button onClick={limparFiltros} variant="outline">
                <X className="h-4 w-4 mr-2" />
                Limpar Filtros
              </Button>
            </div>
          )}
  
          {/* Dados normais */}
          {(!stats || stats.total_alunos > 0 || user?.tipo !== "admin") && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* 🟢 MAIORES PRESENÇAS - Dados Dinâmicos */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg text-green-600">
                    Maiores Presenças
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {stats.maiores_presencas &&
                    stats.maiores_presencas.length > 0 ? (
                      stats.maiores_presencas.map((aluno, index) => (
                        <div
                          key={index}
                          className="flex justify-between items-center p-3 bg-green-50 rounded-lg"
                        >
                          <div>
                            <p className="font-medium">{aluno.nome}</p>
                            <p className="text-sm text-gray-500">{aluno.turma}</p>
                          </div>
                          <div className="text-right">
                            <p className="font-bold text-green-600">
                              {aluno.taxa_presenca}
                            </p>
                            <p className="text-xs text-gray-500">
                              {aluno.aulas_presentes}
                            </p>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="text-center py-4 text-gray-500">
                        <Users className="h-8 w-8 mx-auto mb-2 opacity-50" />
                        <p>Nenhum dado de presença disponível ainda</p>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
  
              {/* 🔴 MAIORES FALTAS - Dados Dinâmicos */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg text-red-600">
                    Maiores Faltas
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {stats.maiores_faltas && stats.maiores_faltas.length > 0 ? (
                      stats.maiores_faltas.map((aluno, index) => (
                        <div
                          key={index}
                          className="flex justify-between items-center p-3 bg-red-50 rounded-lg"
                        >
                          <div>
                            <p className="font-medium">{aluno.nome}</p>
                            <p className="text-sm text-gray-500">{aluno.turma}</p>
                          </div>
                          <div className="text-right">
                            <p className="font-bold text-red-600">
                              {aluno.taxa_presenca}
                            </p>
                            <p className="text-xs text-gray-500">
                              {aluno.faltas}
                            </p>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="text-center py-4 text-gray-500">
                        <AlertCircle className="h-8 w-8 mx-auto mb-2 opacity-50" />
                        <p>Nenhum dado de falta disponível ainda</p>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
  
              {/* 📊 RESUMO GERAL - Dados Dinâmicos */}
              <Card className="md:col-span-2">
                <CardHeader>
                  <CardTitle className="text-lg">
                    Resumo Geral das Suas Turmas
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="text-center p-4 bg-blue-50 rounded-lg relative">
                      <p className="text-2xl font-bold text-blue-600">
                        {typeof stats.taxa_media_presenca === "number"
                          ? `${stats.taxa_media_presenca.toFixed(1)}%`
                          : stats.taxa_media_presenca || "0%"}
                      </p>
                      <p className="text-sm text-gray-600">
                        Taxa Média de Presença
                      </p>
                      {stats.calculo_preciso && (
                        <div className="absolute top-1 right-1">
                          <div
                            className="w-2 h-2 bg-green-500 rounded-full"
                            title="Cálculo Preciso Fase 3"
                          ></div>
                        </div>
                      )}
                    </div>
  
                    <div className="text-center p-4 bg-green-50 rounded-lg relative">
                      <p className="text-2xl font-bold text-green-600">
                        {stats.total_alunos || 0}
                      </p>
                      <p className="text-sm text-gray-600">
                        {stats.regras_aplicadas?.INCLUIR_DESISTENTES_STATS ===
                        false
                          ? "Alunos Ativos"
                          : "Total de Alunos"}
                      </p>
                      {stats.desistentes > 0 && (
                        <p className="text-xs text-gray-500 mt-1">
                          ({stats.desistentes} desistentes)
                        </p>
                      )}
                    </div>
  
                    <div className="text-center p-4 bg-yellow-50 rounded-lg relative">
                      <p className="text-2xl font-bold text-yellow-600">
                        {stats.alunos_em_risco || 0}
                      </p>
                      <p className="text-sm text-gray-600">Alunos em Risco</p>
                      {stats.regras_aplicadas && (
                        <p className="text-xs text-gray-500 mt-1">
                          &lt; {stats.regras_aplicadas.MINIMO_APROVACAO}%
                        </p>
                      )}
                    </div>
  
                    <div className="text-center p-4 bg-red-50 rounded-lg">
                      <p className="text-2xl font-bold text-red-600">
                        {stats.alunos_desistentes || 0}
                      </p>
                      <p className="text-sm text-gray-600">Desistentes</p>
                    </div>
                  </div>
  
                  {/* 🎯 INDICADOR DE PRECISÃO - FASE 3 */}
                  {stats.calculo_preciso && (
                    <div
                      className={`mt-4 p-3 border rounded-lg ${
                        stats.modo_offline
                          ? "bg-orange-50 border-orange-200"
                          : "bg-green-50 border-green-200"
                      }`}
                    >
                      <div className="flex items-center gap-2 text-sm">
                        <div
                          className={`w-2 h-2 rounded-full ${
                            stats.modo_offline ? "bg-orange-500" : "bg-green-500"
                          }`}
                        ></div>
                        <span
                          className={`font-medium ${
                            stats.modo_offline
                              ? "text-orange-800"
                              : "text-green-800"
                          }`}
                        >
                          {stats.modo_offline
                            ? "Cálculo Offline - Fase 3"
                            : "Sistema Fase 3 - Cálculos Precisos"}
                        </span>
                      </div>
                      <div
                        className={`mt-1 text-xs ${
                          stats.modo_offline
                            ? "text-orange-700"
                            : "text-green-700"
                        }`}
                      >
                        <p>• Taxa de presença com precisão de centésimos</p>
                        <p>
                          • Classificação de risco: &lt;
                          {stats.regras_aplicadas?.EM_RISCO}% (risco) | &lt;
                          {stats.regras_aplicadas?.MINIMO_APROVACAO}% (crítico)
                        </p>
                        <p>
                          •{" "}
                          {stats.regras_aplicadas?.INCLUIR_DESISTENTES_STATS
                            ? "Incluindo"
                            : "Excluindo"}{" "}
                          alunos desistentes das médias
                        </p>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
  
              {/* 📋 RESUMO POR TURMA - NOVO */}
              {stats.resumo_turmas && stats.resumo_turmas.length > 0 && (
                <Card className="md:col-span-2">
                  <CardHeader>
                    <CardTitle className="text-lg">Resumo por Turma</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {stats.resumo_turmas.map((turma, index) => (
                        <div key={index} className="p-4 border rounded-lg">
                          <h4 className="font-medium text-lg mb-2">
                            {turma.nome}
                          </h4>
                          <div className="grid grid-cols-3 gap-2 text-sm">
                            <div>
                              <p className="text-gray-600">Alunos</p>
                              <p className="font-bold">{turma.total_alunos}</p>
                            </div>
                            <div>
                              <p className="text-gray-600">Taxa Média</p>
                              <p className="font-bold text-blue-600">
                                {turma.taxa_media}%
                              </p>
                            </div>
                            <div>
                              <p className="text-gray-600">Em Risco</p>
                              <p className="font-bold text-yellow-600">
                                {turma.alunos_risco}
                              </p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    );
  };
  const MotivosManagerButton = () => {
    const { user } = useAuth();
    const { toast } = useToast();
    const [isOpen, setIsOpen] = useState(false);
    const [motivos, setMotivos] = useState([]);
    const [novoMotivo, setNovoMotivo] = useState("");
    const [editingId, setEditingId] = useState(null);
    const [editingDescricao, setEditingDescricao] = useState("");
  
    if (user?.tipo !== "admin") return null;
  
    const fetchMotivos = async () => {
      try {
        const response = await axios.get(`${API}/dropout-reasons/all`);
        setMotivos(Array.isArray(response.data) ? response.data : []);
      } catch {
        setMotivos([]);
      }
    };
  
    const handleOpen = () => {
      fetchMotivos();
      setIsOpen(true);
    };
  
    const handleCreate = async () => {
      if (!novoMotivo.trim()) return;
      try {
        await axios.post(`${API}/dropout-reasons`, { descricao: novoMotivo });
        setNovoMotivo("");
        fetchMotivos();
        toast({ title: "Motivo criado com sucesso!" });
      } catch {
        toast({ title: "Erro ao criar motivo", variant: "destructive" });
      }
    };
  
    const handleUpdate = async (id) => {
      try {
        await axios.put(`${API}/dropout-reasons/${id}`, { descricao: editingDescricao });
        setEditingId(null);
        fetchMotivos();
        toast({ title: "Motivo atualizado!" });
      } catch {
        toast({ title: "Erro ao atualizar", variant: "destructive" });
      }
    };
  
    const handleToggle = async (id, ativo) => {
      try {
        await axios.put(`${API}/dropout-reasons/${id}`, { ativo: !ativo });
        fetchMotivos();
      } catch {
        toast({ title: "Erro ao alterar status", variant: "destructive" });
      }
    };
  
    return (
      <>
        <Button variant="outline" onClick={handleOpen} className="border-purple-400 text-purple-600 hover:bg-purple-50">
          <FileText className="h-4 w-4 mr-2" />
          Motivos
        </Button>
        <Dialog open={isOpen} onOpenChange={setIsOpen}>
          <DialogContent className="max-w-lg max-h-[80vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Gerenciar Motivos de Desistência</DialogTitle>
              <DialogDescription>Crie e gerencie os motivos disponíveis para registro de desistência.</DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div className="flex gap-2">
                <Input
                  value={novoMotivo}
                  onChange={(e) => setNovoMotivo(e.target.value)}
                  placeholder="Novo motivo..."
                  onKeyDown={(e) => e.key === "Enter" && handleCreate()}
                />
                <Button onClick={handleCreate} className="bg-blue-600 hover:bg-blue-700">
                  <Plus className="h-4 w-4" />
                </Button>
              </div>
              <div className="space-y-2">
                {motivos.map((motivo) => (
                  <div key={motivo.id} className={`flex items-center gap-2 p-2 border rounded-lg ${!motivo.ativo ? "opacity-50 bg-gray-50" : ""}`}>
                    {editingId === motivo.id ? (
                      <>
                        <Input value={editingDescricao} onChange={(e) => setEditingDescricao(e.target.value)} className="flex-1" />
                        <Button size="sm" onClick={() => handleUpdate(motivo.id)} className="bg-green-600 hover:bg-green-700"><Save className="h-4 w-4" /></Button>
                        <Button size="sm" variant="outline" onClick={() => setEditingId(null)}><X className="h-4 w-4" /></Button>
                      </>
                    ) : (
                      <>
                        <span className="flex-1 text-sm">{motivo.descricao}</span>
                        <Badge variant={motivo.ativo ? "default" : "secondary"}>{motivo.ativo ? "Ativo" : "Inativo"}</Badge>
                        <Button size="sm" variant="outline" onClick={() => { setEditingId(motivo.id); setEditingDescricao(motivo.descricao); }}><Edit className="h-4 w-4" /></Button>
                        <Button size="sm" variant="outline" onClick={() => handleToggle(motivo.id, motivo.ativo)} className="text-orange-600"><EyeOff className="h-4 w-4" /></Button>
                      </>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </>
    );
  };

  // ============================================================
// 🔄 COMPONENTE: Transferir aluno de turma
// ============================================================
const TransferirTurmaPanel = ({ aluno, turmas, onTransferido }) => {
  const { toast } = useToast();
  const [novaTurmaId, setNovaTurmaId] = useState("");
  const [transferindo, setTransferindo] = useState(false);

  const turmaAtual = turmas.find(t =>
    Array.isArray(t.alunos_ids) &&
    t.alunos_ids.map(String).includes(String(aluno?.id))
  );

  const turmasDisponiveis = turmas.filter(t =>
    t.id !== turmaAtual?.id && t.ativo !== false
  );

  const handleTransferir = async () => {
    if (!novaTurmaId) return;

    if (novaTurmaId === "sem_turma") {
      // Só remove da turma atual
      if (!turmaAtual) return;
      setTransferindo(true);
      try {
        await axios.delete(`${API}/classes/${turmaAtual.id}/students/${aluno.id}`);
        toast({ title: "Aluno removido da turma com sucesso!" });
        setNovaTurmaId("");
        onTransferido();
      } catch (error) {
        toast({
          title: "Erro ao remover da turma",
          description: error.response?.data?.detail || "Tente novamente",
          variant: "destructive",
        });
      } finally {
        setTransferindo(false);
      }
      return;
    }

    setTransferindo(true);
    try {
      if (turmaAtual) {
        await axios.delete(`${API}/classes/${turmaAtual.id}/students/${aluno.id}`);
      }
      await axios.put(`${API}/classes/${novaTurmaId}/students/${aluno.id}`);
      toast({
        title: "✅ Transferência realizada!",
        description: `${aluno.nome} foi transferido com sucesso.`,
      });
      setNovaTurmaId("");
      onTransferido();
    } catch (error) {
      toast({
        title: "Erro na transferência",
        description: error.response?.data?.detail || "Tente novamente",
        variant: "destructive",
      });
    } finally {
      setTransferindo(false);
    }
  };

  return (
    <div className="space-y-4">
      {turmaAtual ? (
        <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-sm font-medium text-blue-800 mb-2">Situação atual</p>
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div>
              <p className="text-gray-500 text-xs">Turma</p>
              <p className="font-medium">{turmaAtual.nome}</p>
            </div>
            <div>
              <p className="text-gray-500 text-xs">Ciclo</p>
              <p className="font-medium">{turmaAtual.ciclo || "—"}</p>
            </div>
            <div>
              <p className="text-gray-500 text-xs">Horário</p>
              <p className="font-medium">{turmaAtual.horario_inicio} – {turmaAtual.horario_fim}</p>
            </div>
            <div>
              <p className="text-gray-500 text-xs">Vagas ocupadas</p>
              <p className="font-medium">{turmaAtual.alunos_ids?.length || 0}/{turmaAtual.vagas_total}</p>
            </div>
          </div>
        </div>
      ) : (
        <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg text-sm text-yellow-800">
          Este aluno não está alocado em nenhuma turma.
        </div>
      )}

      <div className="space-y-3">
        <Label className="font-medium">Transferir para outra turma</Label>
        <Select value={novaTurmaId} onValueChange={setNovaTurmaId}>
          <SelectTrigger>
            <SelectValue placeholder="Selecione a turma de destino" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="sem_turma">Remover da turma (sem realocar)</SelectItem>
            {turmasDisponiveis.map(t => (
              <SelectItem key={t.id} value={t.id}>
                {t.nome} — {t.ciclo || "sem ciclo"} ({t.alunos_ids?.length || 0}/{t.vagas_total} vagas)
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        {novaTurmaId && novaTurmaId !== "sem_turma" && (
          <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg text-xs text-yellow-800">
            ⚠️ O aluno será removido da turma atual. O histórico de chamadas é mantido.
          </div>
        )}

        <Button
          onClick={handleTransferir}
          disabled={!novaTurmaId || transferindo}
          className="w-full bg-blue-600 hover:bg-blue-700"
        >
          {transferindo ? (
            <span className="flex items-center gap-2">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              Transferindo...
            </span>
          ) : "Confirmar transferência"}
        </Button>
      </div>
    </div>
  );
};

// ============================================================
// 📊 COMPONENTE: Frequência do aluno
// ============================================================
const FrequenciaAlunoPanel = ({ alunoId }) => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!alunoId) return;
    axios.get(`${API}/reports/teacher-stats`)
      .then(res => {
        const found = res.data?.detalhes_por_aluno?.find(
          a => String(a.id) === String(alunoId)
        );
        setStats(found || null);
      })
      .catch(() => setStats(null))
      .finally(() => setLoading(false));
  }, [alunoId]);

  if (loading) return (
    <div className="text-center py-8 text-gray-500">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
      Carregando frequência...
    </div>
  );

  if (!stats) return (
    <div className="text-center py-8 text-gray-500">
      <BarChart3 className="h-12 w-12 mx-auto mb-3 text-gray-300" />
      <p>Sem dados de frequência ainda.</p>
      <p className="text-sm mt-1">Este aluno ainda não possui chamadas registradas.</p>
    </div>
  );

  const pct = stats.percentualPresenca || 0;
  const risco = pct >= 75 ? "adequado" : pct >= 60 ? "em_risco" : "critico";
  const corRisco = {
    adequado: "text-green-600",
    em_risco: "text-yellow-600",
    critico: "text-red-600"
  }[risco];
  const labelRisco = {
    adequado: "✅ Frequência adequada (≥75%)",
    em_risco: "⚠️ Aluno em risco (60–74%)",
    critico: "🚨 Situação crítica (<60%)"
  }[risco];
  const bgRisco = {
    adequado: "bg-green-50 text-green-800 border border-green-200",
    em_risco: "bg-yellow-50 text-yellow-800 border border-yellow-200",
    critico: "bg-red-50 text-red-800 border border-red-200"
  }[risco];

  const faltas = (stats.totalChamadas || 0) - (stats.presencas || 0);

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div className="bg-gray-50 rounded-lg p-4 text-center">
          <p className={`text-2xl font-bold ${corRisco}`}>{pct.toFixed(1)}%</p>
          <p className="text-xs text-gray-500 mt-1">Frequência</p>
        </div>
        <div className="bg-gray-50 rounded-lg p-4 text-center">
          <p className="text-2xl font-bold text-green-600">{stats.presencas || 0}</p>
          <p className="text-xs text-gray-500 mt-1">Presenças</p>
        </div>
        <div className="bg-gray-50 rounded-lg p-4 text-center">
          <p className="text-2xl font-bold text-red-600">{faltas}</p>
          <p className="text-xs text-gray-500 mt-1">Faltas</p>
        </div>
        <div className="bg-gray-50 rounded-lg p-4 text-center">
          <p className="text-2xl font-bold text-gray-700">{stats.totalChamadas || 0}</p>
          <p className="text-xs text-gray-500 mt-1">Total de aulas</p>
        </div>
      </div>

      <div className={`p-3 rounded-lg text-sm font-medium ${bgRisco}`}>
        {labelRisco}
      </div>
    </div>
  );
};
  
  // Alunos Manager Component COMPLETO
  const AlunosManager = (props) => {
    const { user } = useAuth(); // 🔧 HOOK ORDER FIX: useAuth deve vir primeiro
    const { toast } = useToast();
  
    const [alunos, setAlunos] = useState([]);
    const [loading, setLoading] = useState(true);
    const [isDialogOpen, setIsDialogOpen] = useState(false);
    const [editingAluno, setEditingAluno] = useState(null);
    const [isDropoutDialogOpen, setIsDropoutDialogOpen] = useState(false);
    const [isAtestadoDialogOpen, setIsAtestadoDialogOpen] = useState(false);
    const [selectedAluno, setSelectedAluno] = useState(null);
    const [dropoutReason, setDropoutReason] = useState("");
    const [selectedFile, setSelectedFile] = useState(null);
    const [turmas, setTurmas] = useState([]);
  
    // Estados para visualização detalhada do aluno
    const [isViewAlunoDialogOpen, setIsViewAlunoDialogOpen] = useState(false);
    const [viewingAluno, setViewingAluno] = useState(null);
    const [studentJustifications, setStudentJustifications] = useState([]);
    const [loadingJustifications, setLoadingJustifications] = useState(false);
  
    // 🚀 BULK UPLOAD STATES
    const [isBulkUploadOpen, setIsBulkUploadOpen] = useState(false);
    const [bulkUploadFile, setBulkUploadFile] = useState(null);
    const [updateExisting, setUpdateExisting] = useState(false);
    const [selectedTurmaForBulk, setSelectedTurmaForBulk] = useState("");
    const [bulkUploading, setBulkUploading] = useState(false);
    const [showBulkSummary, setShowBulkSummary] = useState(false);
    const [bulkSummaryData, setBulkSummaryData] = useState(null);
    const [dropoutReasons, setDropoutReasons] = useState([]);
    const [isReativacaoDialogOpen, setIsReativacaoDialogOpen] = useState(false);
    const [reativacaoAluno, setReativacaoAluno] = useState(null);
    const [reativacaoMotivo, setReativacaoMotivo] = useState("");
    const [reativacaoSaving, setReativacaoSaving] = useState(false);
    const [selectedDropoutReason, setSelectedDropoutReason] = useState("");
  
    const [formData, setFormData] = useState({
    nome: "",
    cpf: "",
    nome_social: "",
    turma_id: "",
    });
    const { filtros, setFiltros } = props;
    const filtroBusca = filtros.busca;
    const filtroCurso = filtros.curso;
    const filtroTurma = filtros.turma;
    const [cursos, setCursos] = useState([]);
    const fetchDropoutReasons = async () => {
    try {
      const response = await axios.get(`${API}/dropout-reasons`);
      setDropoutReasons(Array.isArray(response.data) ? response.data :[]);
    } catch (error) {
      setDropoutReasons([]);
    }
  };
    
      useEffect(() => {
      if (user) {
        fetchAlunos();
        fetchTurmas();
        fetchCursos();
        fetchDropoutReasons();
    }
    },     [user]);

  // 👇 FUNÇÃO PARA BUSCAR CURSOS (CORRIGIDA) 👇
  const fetchCursos = async () => {
    try {
      const response = await axios.get(`${API}/courses`);
      setCursos(Array.isArray(response.data) ? response.data :[]);
    } catch (error) {
      console.error("❌ Erro ao buscar cursos:", error);
      setCursos([]);
    }
  };

  // 👇 FUNÇÃO PARA BUSCAR ALUNOS COM LIMITE AUMENTADO PARA 5000 👇
// ✅ CORRETO — com catch completo
const fetchAlunos = async () => {
  try {
    console.log("🔍 Buscando alunos...");
    const params = new URLSearchParams({ limit: 5000 });
    if (user?.tipo === "instrutor" && user?.curso_id) {
      params.append("curso_id", user.curso_id);
    }

    const response = await axios.get(`${API}/students?${params}`);
    console.log("✅ Alunos recebidos:", response.data.length, "alunos");

    const alunosOrdenados = Array.isArray(response.data)
      ? response.data.sort((a, b) => a.nome.localeCompare(b.nome, "pt-BR"))
      : [];
    setAlunos(alunosOrdenados);
  } catch (error) {
    console.error("❌ Erro ao buscar alunos:", error);
    setAlunos([]);
    toast({
      title: "Erro ao carregar alunos",
      description: "Não foi possível carregar a lista de alunos",
      variant: "destructive",
    });
  } finally {
    setLoading(false);
  }
};
  
      const fetchTurmas = async () => {       
      try {
        console.log("🔍 Buscando turmas...");
        const response = await axios.get(`${API}/classes`);
        console.log("✅ Turmas recebidas:", response.data.length, "turmas");
        setTurmas(Array.isArray(response.data) ? response.data : []);
      } catch (error) {
        console.error("❌ Erro ao buscar turmas:", error);
        setTurmas([]);
        toast({
          title: "Erro ao carregar turmas",
          description: "Não foi possível carregar a lista de turmas",
          variant: "destructive",
        });
      } finally {
      setLoading(false);
      }
    };
  
    const handleSubmit = async (e) => {
      e.preventDefault();
  
      // ✅ VALIDAÇÃO: Campos obrigatórios
      if (!formData.nome.trim()) {
        toast({
          title: "Campo obrigatório",
          description: "Nome completo é obrigatório",
          variant: "destructive",
        });
        return;
      }
  
      if (!formData.cpf.trim()) {
        toast({
          title: "Campo obrigatório",
          description: "CPF é obrigatório",
          variant: "destructive",
        });
        return;
      }
  
       try {
  if (editingAluno) {
    const nomeSocialLimpo = formData.nome_social?.trim();
    const updatePayload = {
      nome: formData.nome,
      cpf: formData.cpf,
      nome_social: (nomeSocialLimpo && nomeSocialLimpo !== "-") ? nomeSocialLimpo : null,
    };
    await axios.put(`${API}/students/${editingAluno.id}`, updatePayload);
    toast({
      title: "Aluno atualizado com sucesso!",
      description: "As informações do aluno foram atualizadas.",
    });
        } else {
          const response = await axios.post(`${API}/students`, formData);
          const novoAlunoId = response.data.id;
  
          // Se turma foi selecionada (e não é "sem_turma"), adicionar aluno à turma
          if (formData.turma_id && formData.turma_id !== "sem_turma") {
            try {
              await axios.put(
                `${API}/classes/${formData.turma_id}/students/${novoAlunoId}`,
              );
              toast({
                title: "Aluno criado e alocado com sucesso!",
                description:
                  "O aluno foi adicionado ao sistema e à turma selecionada.",
              });
            } catch (turmaError) {
              console.error("Erro ao adicionar aluno à turma:", turmaError);
              toast({
                title: "Aluno criado, mas erro na alocação",
                description:
                  "Aluno criado com sucesso, mas não foi possível adicioná-lo à turma. Faça isso manualmente.",
                variant: "destructive",
              });
            }
          } else {
            toast({
              title: "Aluno criado com sucesso!",
              description:
                "O novo aluno foi adicionado ao sistema (sem turma específica).",
            });
          }
        }
  
        // Fechar modal primeiro
        setIsDialogOpen(false);
  
        // Aguardar o modal fechar antes de atualizar estados
        setTimeout(() => {
          setEditingAluno(null);
          resetForm();
          fetchAlunos();
        }, 100);
      } catch (error) {
        toast({
          title: editingAluno ? "Erro ao atualizar aluno" : "Erro ao criar aluno",
          description: error.response?.data?.detail || "Tente novamente",
          variant: "destructive",
        });
      }
    };
  
  const resetForm = () => {
    setFormData({
      nome: "",
      cpf: "",
      nome_social: "",
      turma_id: "",
      });
    };
  
    const handleViewAluno = (aluno) => {
      setViewingAluno(aluno);
      setIsViewAlunoDialogOpen(true);
      fetchStudentJustifications(aluno.id);
    };
  
    const fetchStudentJustifications = async (studentId) => {
      try {
        setLoadingJustifications(true);
        const response = await axios.get(
          `${API}/students/${studentId}/justifications`,
        );
        setStudentJustifications(response.data);
      } catch (error) {
        console.error("Erro ao carregar justificativas:", error);
        setStudentJustifications([]);
      } finally {
        setLoadingJustifications(false);
      }
    };
  
    const downloadJustificationFile = async (justificationId, filename) => {
      try {
        const response = await axios.get(
          `${API}/justifications/${justificationId}/file`,
          {
            responseType: "blob",
          },
        );
  
        const blob = new Blob([response.data]);
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = filename || "documento";
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
  
        toast({
          title: "Sucesso",
          description: "Arquivo baixado com sucesso!",
        });
      } catch (error) {
        console.error("Erro ao baixar arquivo:", error);
        toast({
          title: "Erro",
          description: "Erro ao baixar arquivo",
          variant: "destructive",
        });
      }
    };
  
    const deleteJustification = async (justificationId) => {
      try {
        await axios.delete(`${API}/justifications/${justificationId}`);
  
        toast({
          title: "Sucesso",
          description: "Justificativa removida com sucesso!",
        });
  
        // Recarregar justificativas
        if (viewingAluno) {
          fetchStudentJustifications(viewingAluno.id);
        }
      } catch (error) {
        console.error("Erro ao remover justificativa:", error);
        toast({
          title: "Erro",
          description: "Erro ao remover justificativa",
          variant: "destructive",
        });
      }
    };
  
    const handleEdit = (aluno) => {
      setEditingAluno(aluno);
      setFormData({
       nome: aluno.nome,
       cpf: aluno.cpf,
       nome_social: (aluno.nome_social && aluno.nome_social !== "-") ? aluno.nome_social : "",       turma_id: "",
      });
      setIsDialogOpen(true);
    };
  
    const handleOpenDialog = () => {
      setEditingAluno(null);
      resetForm();
      setIsDialogOpen(true);
    };
  
    const handleMarkAsDropout = (aluno) => {
      setSelectedAluno(aluno);
      setDropoutReason("");
      setSelectedDropoutReason("");
      setIsDropoutDialogOpen(true);
    };
  
    const handleUploadAtestado = (aluno) => {
      setSelectedAluno(aluno);
      setSelectedFile(null);
      setIsAtestadoDialogOpen(true);
    };
  
  const submitDropout = async () => {
      if (!selectedDropoutReason) {
        toast({
          title: "Motivo obrigatório",
          description: "Por favor, selecione o motivo da desistência.",
          variant: "destructive",
        });
        return;
      }
  
      if (selectedDropoutReason === "outro" && !dropoutReason.trim()) {
        toast({
          title: "Motivo obrigatório",
          description: "Por favor, descreva o motivo.",
          variant: "destructive",
        });
        return;
      }
  
      const motivoSelecionado = dropoutReasons.find(m => m.id === selectedDropoutReason);
      const descricaoFinal = selectedDropoutReason === "outro"
        ? dropoutReason
        : motivoSelecionado?.descricao || dropoutReason;
  
      try {
        await axios.post(`${API}/dropouts`, {
          aluno_id: selectedAluno.id,
          motivo_codigo: selectedDropoutReason === "outro" ? "outro" : selectedDropoutReason,
          motivo_descricao: descricaoFinal,
          data_desistencia: new Date().toISOString().split("T")[0],
          turma_id: (() => {
            const turmaEncontrada = turmas.find(t =>
              Array.isArray(t.alunos_ids) &&
              t.alunos_ids.map(String).includes(String(selectedAluno.id))
            );
            return turmaEncontrada?.id || selectedAluno.turma_id || (selectedAluno.turmas_ids?.[0] ?? null);
          })(),
          });
  
        await axios.put(`${API}/students/${selectedAluno.id}`, {
          ...selectedAluno,
          status: "desistente",
        });
  
        toast({
          title: "Desistência registrada",
          description: `${selectedAluno.nome} foi marcado como desistente.`,
        });
  
        fetchAlunos();
        setIsDropoutDialogOpen(false);
        setSelectedAluno(null);
        setDropoutReason("");
      } catch (error) {
        console.error("Error marking as dropout:", error);
        toast({
          title: "Erro ao registrar desistência",
          description: error.response?.data?.detail || "Tente novamente",
          variant: "destructive",
        });
      }
    };
      const handleSolicitarReativacao = (aluno) => {
  setReativacaoAluno(aluno);
  setReativacaoMotivo("");
  setIsReativacaoDialogOpen(true);
};

    const submitReativacao = async () => {
      setReativacaoSaving(true);
      try {
        const params = reativacaoMotivo.trim()
          ? `?motivo=${encodeURIComponent(reativacaoMotivo)}`
          : "";
        await axios.post(`${API}/students/${reativacaoAluno.id}/reactivation-request${params}`);
        toast({
          title: "✅ Solicitação enviada!",
          description: "O administrador receberá a solicitação para reativar o aluno.",
        });
        setIsReativacaoDialogOpen(false);
        setReativacaoAluno(null);
        setReativacaoMotivo("");
      } catch (error) {
        toast({
          title: "Erro ao enviar solicitação",
          description: error.response?.data?.detail || "Tente novamente",
          variant: "destructive",
        });
      } finally {
        setReativacaoSaving(false);
      }
    };                     
        
    const submitAtestado = async () => {
      if (!selectedFile) {
        toast({
          title: "Arquivo obrigatório",
          description: "Por favor, selecione um arquivo de atestado.",
          variant: "destructive",
        });
        return;
      }
  
      try {
        const formData = new FormData();
        formData.append("file", selectedFile);
        formData.append("aluno_id", selectedAluno.id);
        formData.append("tipo", "atestado_medico");
  
        await axios.post(`${API}/upload/atestado`, formData, {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        });
  
        toast({
          title: "Atestado enviado",
          description: `Atestado médico de ${selectedAluno.nome} foi registrado.`,
        });
  
        setIsAtestadoDialogOpen(false);
        setSelectedAluno(null);
        setSelectedFile(null);
      } catch (error) {
        console.error("Error uploading atestado:", error);
        toast({
          title: "Erro ao enviar atestado",
          description: error.response?.data?.detail || "Tente novamente",
          variant: "destructive",
        });
      }
    };
  
    // 🚀 BULK UPLOAD FUNCTIONS
    const handleBulkUpload = async () => {
      if (!bulkUploadFile) {
        toast({
          title: "Arquivo obrigatório",
          description: "Por favor, selecione um arquivo CSV ou Excel",
          variant: "destructive",
        });
        return;
      }
  
      setBulkUploading(true);
  
      try {
        const formData = new FormData();
        formData.append("file", bulkUploadFile);
  
        // Construir parâmetros
        const params = new URLSearchParams();
        if (updateExisting) params.append("update_existing", "true");
        if (selectedTurmaForBulk && selectedTurmaForBulk !== "sem_turma_padrao") {
          params.append("turma_id", selectedTurmaForBulk);
        }
  
        console.log("🚀 Iniciando bulk upload...");
        console.log("📄 Arquivo:", bulkUploadFile.name);
        console.log("🔄 Atualizar existentes:", updateExisting);
        console.log("🎯 Turma selecionada:", selectedTurmaForBulk);
  
        const response = await axios.post(
          `${API}/students/bulk-upload?${params}`,
          formData,
          {
            headers: { "Content-Type": "multipart/form-data" },
            timeout: 300000, // 5 minutos para uploads grandes
          },
        );
  
        const result = response.data;
        console.log("✅ Upload concluído:", result);
  
        // Mostrar resumo
        setBulkSummaryData(result);
        setShowBulkSummary(true);
  
        // Fechar dialog de upload
        setIsBulkUploadOpen(false);
  
        // Limpar campos
        setBulkUploadFile(null);
        setUpdateExisting(false);
        setSelectedTurmaForBulk("");
  
        // Recarregar alunos
        fetchAlunos();
  
        toast({
          title: "✅ Upload Concluído",
          description: result.message,
        });
      } catch (error) {
        console.error("❌ Erro no bulk upload:", error);
        toast({
          title: "❌ Erro no Upload",
          description: error.response?.data?.detail || error.message,
          variant: "destructive",
        });
      } finally {
        setBulkUploading(false);
      }
    };
  
    const downloadErrorReport = (errors) => {
      const csvContent = [
        "linha,erro,dados",
        ...errors.map(
          (error) =>
            `${error.line},"${error.error}","${JSON.stringify(error.data || {})}"`,
        ),
      ].join("\n");
  
      const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = `erros_bulk_upload_${
        new Date().toISOString().split("T")[0]
      }.csv`;
      link.click();
      URL.revokeObjectURL(link.href);
    };
  
    const downloadTemplate = () => {
      const templateContent = `nome_completo,nome_social,cpf
  João da Silva,,123.456.789-09
  Maria Souza,Mari,987.654.321-00
  Carlos Pereira,,111.222.333-44`;
  
      const blob = new Blob([templateContent], {
        type: "text/csv;charset=utf-8;",
      });
      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = "modelo_alunos.csv";
      link.click();
      URL.revokeObjectURL(link.href);
    };
  
    const getStatusColor = (status) => {
      const colors = {
        ativo: "default",
        desistente: "destructive",
        concluido: "secondary",
        suspenso: "outline",
      };
      return colors[status] || "default";
    };
  
    const getStatusLabel = (status) => {
      const labels = {
        ativo: "Ativo",
        desistente: "Desistente",
        concluido: "Concluído",
        suspenso: "Suspenso",
      };
      return labels[status] || status;
    };
  
    // 🎯 PRODUÇÃO: Função de debug removida
  
    // 🎯 PRODUÇÃO: Função de debug removida
  
    // 🎯 PRODUÇÃO: Função de debug removida
  
    // 🎯 PRODUÇÃO: Função de debug removida
  
    if (loading)
      return (
        <div key="alunos-loading" className="p-8 text-center">
          Carregando alunos...
        </div>
      );
  
    return (
      <Card key="alunos-content">
        <CardHeader>
          <div className="flex justify-between items-center">
            <div>
              <CardTitle>Gerenciamento de Alunos</CardTitle>
              <CardDescription>
                {user?.tipo === "admin"
                  ? "Gerencie todos os alunos cadastrados no sistema"
                  : `Gerencie alunos das suas turmas (${
                      user?.curso_nome || "seu curso"
                    })`}
              </CardDescription>
            </div>
            <div className="flex gap-2">
              {user?.tipo === "admin" && <MotivosManagerButton />}
              {/* 🚀 BULK UPLOAD BUTTON */}
                {user?.tipo !== "monitor" && (
                <Button
                  onClick={() => setIsBulkUploadOpen(true)}
                  className="bg-green-600 hover:bg-green-700"
                >
                  <Upload className="h-4 w-4 mr-2" />
                  Importar em Massa
                </Button>
              )}      
  
              {/* 🎯 PRODUÇÃO: Botões de teste removidos para usuários finais */}
              <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
                <DialogTrigger asChild>
                  <Button
                    onClick={handleOpenDialog}
                    className="bg-blue-600 hover:bg-blue-700"
                  >
                    <Plus className="h-4 w-4 mr-2" />
                    Novo Aluno
                  </Button>
                </DialogTrigger>
                <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
                  <DialogHeader>
                    <DialogTitle>
                      {editingAluno ? "Editar Aluno" : "Cadastrar Novo Aluno"}
                    </DialogTitle>
                    <DialogDescription>
                      {editingAluno
                        ? "Atualize os dados do aluno"
                        : "Preencha os dados para cadastrar um novo aluno"}
                    </DialogDescription>
                  </DialogHeader>
                  <form onSubmit={handleSubmit} className="space-y-4">
                    {/* Campos Obrigatórios - Destacados */}
  <div className="border-2 border-blue-200 rounded-lg p-4 bg-blue-50">
                      <h3 className="text-lg font-semibold text-blue-800 mb-3">
                        📋 Cadastro do aluno
                      </h3>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="space-y-2">
                          <Label
                            htmlFor="nome"
                            className="text-blue-700 font-medium"
                          >
                            Nome Completo *
                          </Label>
                          <Input
                            id="nome"
                            value={formData.nome}
                            onChange={(e) =>
                              setFormData({ ...formData, nome: e.target.value })
                            }
                            placeholder="Ex: João Silva Santos"
                            className="border-blue-300 focus:border-blue-500"
                            required
                          />
                        </div>
  
                        <div className="space-y-2">
                          <Label
                            htmlFor="nome_social"
                            className="text-blue-700 font-medium"
                          >
                            Nome Social
                          </Label>
                          <Input
                            id="nome_social"
                            value={formData.nome_social}
                            onChange={(e) =>
                              setFormData({ ...formData, nome_social: e.target.value })
                            }
                            placeholder="Ex: Mari"
                            className="border-blue-300 focus:border-blue-500"
                          />
                        </div>
  
                        <div className="space-y-2">
                          <Label
                            htmlFor="cpf"
                            className="text-blue-700 font-medium"
                          >
                            CPF *
                          </Label>
                          <Input
                            id="cpf"
                            value={formData.cpf}
                            onChange={(e) =>
                              setFormData({ ...formData, cpf: e.target.value })
                            }
                            placeholder="000.000.000-00"
                            className="border-blue-300 focus:border-blue-500"
                            required
                          />
                        </div>
                      </div>
                    </div>
                    {/* Campo Turma - Entre Obrigatórios e Complementares */}
                    <div className="border-2 border-green-200 rounded-lg p-4 bg-green-50">
                      <h3 className="text-lg font-semibold text-green-800 mb-3">
                        🎯 Alocação em Turma
                      </h3>
                      <div className="space-y-2">
                        <Label
                          htmlFor="turma_id"
                          className="text-green-700 font-medium"
                        >
                          Turma (Opcional)
                        </Label>
                        <Select
                          value={formData.turma_id}
                          onValueChange={(value) =>
                            setFormData({ ...formData, turma_id: value })
                          }
                        >
                          <SelectTrigger className="border-green-300 focus:border-green-500">
                            <SelectValue placeholder="Selecione uma turma ou deixe em branco" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="sem_turma">
                              Sem turma (não alocado)
                            </SelectItem>
                            {Array.isArray(turmas) &&
                              turmas.map((turma) => (
                                <SelectItem key={turma.id} value={turma.id}>
                                  {turma.nome} -{" "}
                                  {turma.curso_nome || "Curso não informado"}
                                </SelectItem>
                              ))}
                          </SelectContent>
                        </Select>
                        <p className="text-xs text-green-600">
                          💡 Você pode deixar sem turma e alocar depois, ou
                          selecionar uma turma específica
                        </p>
                      </div>
                    </div>
                                        
                    <Button
                      type="submit"
                      className="w-full bg-blue-600 hover:bg-blue-700"
                    >
                      <Save className="h-4 w-4 mr-2" />
                      {editingAluno ? "Atualizar Aluno" : "Cadastrar Aluno"}
                    </Button>
                  </form>
                </DialogContent>
              </Dialog>
            </div>
          </div>
        </CardHeader>
  
        {/* Card de Permissões para Usuários Não-Admin */}
        {user?.tipo !== "admin" && (
          <div className="mx-6 mb-4 p-4 bg-orange-50 border border-orange-200 rounded-lg">
            <div className="flex items-center gap-2 text-orange-800">
              <Info className="h-4 w-4" />
              <span className="text-sm font-medium">Suas Permissões:</span>
            </div>
            <div className="mt-2 text-sm text-orange-700">
              <p>
                • <strong>Tipo:</strong>{" "}
                {user.tipo?.charAt(0).toUpperCase() + user.tipo?.slice(1)}
              </p>
              <p>
                • <strong>Unidade:</strong> {user?.unidade_nome || "Sua unidade"}
              </p>
              <p>
                • <strong>Curso:</strong> {user?.curso_nome || "Seu curso"}
              </p>
              <p>
                • <strong>Escopo:</strong>{" "}
                {user?.tipo === "instrutor"
                  ? "Alunos do seu curso específico"
                  : user?.tipo === "pedagogo"
                    ? "Todos os alunos da sua unidade"
                    : "Alunos das turmas que você monitora"}
              </p>
              <p>
                • <strong>CSV:</strong>{" "}
                {user?.tipo === "instrutor"
                  ? "Pode importar apenas do seu curso"
                  : user?.tipo === "pedagogo"
                    ? "Pode importar de qualquer curso da unidade"
                    : "Não pode importar (apenas visualizar)"}
              </p>
              {user?.tipo === "instrutor" && (
                <div className="mt-2 p-2 bg-blue-50 border border-blue-200 rounded text-xs text-blue-700">
                  <p className="font-medium">💡 Dicas para Instrutores:</p>
                  <p>
                    • Turmas inexistentes no CSV serão criadas automaticamente
                  </p>
                  <p>• Alunos sem turma definida ficarão como "não alocado"</p>
                  <p>• Você pode gerenciar alunos entre suas turmas</p>
                </div>
              )}
            </div>
          </div>
        )}
  
<CardContent>
  {/* 🔍 FILTROS AVANÇADOS DE ALUNOS */}
          <div className="mb-4 p-4 bg-gray-50 border rounded-lg">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
              <div className="space-y-1">
                <Label className="text-sm">Buscar por nome ou CPF</Label>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    placeholder="Nome ou CPF..."
                    value={filtroBusca}
                    onChange={(e) => setFiltros({ ...filtros, busca: e.target.value })}
                    className="pl-9"
                  />
                </div>
              </div>
              <div className="space-y-1">
                <Label className="text-sm">Curso</Label>
                <Select value={filtroCurso} onValueChange={(v) => setFiltros({ ...filtros, curso: v })}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="todos">Todos</SelectItem>
                    {Array.isArray(cursos) && cursos.map((c) => (
                      <SelectItem key={c.id} value={c.id}>{c.nome}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-1">
                <Label className="text-sm">Turma</Label>
                <Select value={filtroTurma} onValueChange={(v) => setFiltros({ ...filtros, turma: v })}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="todos">Todas</SelectItem>
                    {Array.isArray(turmas) && turmas.map((t) => (
                      <SelectItem key={t.id} value={t.id}>{t.nome}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="flex items-end">
                <Button 
                  variant="outline" 
                  className="w-full" 
                  onClick={() => setFiltros({ busca: "", curso: "todos", turma: "todos" })}
                >
                  <X className="h-4 w-4 mr-1" /> Limpar Filtros
                </Button>
              </div>
            </div>
          </div>

          <div className="table-container">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Nome</TableHead>
                  <TableHead>CPF</TableHead>
                  <TableHead>Nome Social</TableHead>
                  <TableHead>Contato</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Ações</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
              {Array.isArray(alunos) &&
                  alunos
           .filter((aluno) => {
           let buscaOk = true;
           if (filtroBusca.trim()) {
           const termoBusca = filtroBusca.toLowerCase().trim();
           const termoCPF = filtroBusca.replace(/\D/g, "");

           const nomeBate = (aluno.nome || "").toLowerCase().includes(termoBusca);
           const nomeSocialBate = (aluno.nome_social || "").toLowerCase().includes(termoBusca);
           const cpfBate = termoCPF.length > 0
            ? (aluno.cpf || "").replace(/\D/g, "").includes(termoCPF)
            : false;

    buscaOk = nomeBate || nomeSocialBate || cpfBate;
  }

const cursoOk = filtroCurso === "todos" ||
    turmas.some(t =>
      String(t.curso_id) === String(filtroCurso) &&
      Array.isArray(t.alunos_ids) &&
      t.alunos_ids.map(String).includes(String(aluno.id))
    );

  const turmaOk = filtroTurma === "todos" ||
    turmas.some(t =>
      String(t.id) === String(filtroTurma) &&
      Array.isArray(t.alunos_ids) &&
      t.alunos_ids.map(String).includes(String(aluno.id))
    );

  return buscaOk && cursoOk && turmaOk;
})
                    .map((aluno) => (
                      
                      <TableRow key={aluno.id}>
                      <TableCell className="font-medium">{aluno.nome}</TableCell>
                      <TableCell>{aluno.cpf}</TableCell>
                      <TableCell className="text-center font-medium">
                        {aluno.nome_social || "—"}
                      </TableCell>
                      <TableCell>
                        <div className="space-y-1">
                          {aluno.telefone && (
                            <div className="flex items-center text-sm">
                              <Phone className="h-3 w-3 mr-1 text-gray-400" />
                              {aluno.telefone}
                            </div>
                          )}
                          {aluno.email && (
                            <div className="flex items-center text-sm">
                              <Mail className="h-3 w-3 mr-1 text-gray-400" />
                              {aluno.email}
                            </div>
                          )}
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant={getStatusColor(aluno.status)}>
                          {getStatusLabel(aluno.status)}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex space-x-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleViewAluno(aluno)}
                            title="Visualizar detalhes"
                          >
                            <Eye className="h-4 w-4" />
                          </Button>
                          {aluno.status !== "desistente" && (
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleEdit(aluno)}
                              title="Editar aluno"
                            >
                              <Edit className="h-4 w-4" />
                            </Button>
                          )}
                            {aluno.status === "ativo" && (
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleMarkAsDropout(aluno)}
                              title="Registrar desistência"
                              className="text-red-600 border-red-600 hover:bg-red-50"
                            >
                                <UserX className="h-4 w-4" />
                              </Button>
                            )}
                            {aluno.status === "desistente" && (
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleSolicitarReativacao(aluno)}
                                title="Solicitar reativação"
                                className="text-green-600 border-green-600 hover:bg-green-50"
                              >
                                <RefreshCw className="h-4 w-4" />
                              </Button>
                            )}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
        </TableBody>
            </Table>
          </div>
        </CardContent>

        {/* Dialog para registrar desistência */}
        <Dialog open={isDropoutDialogOpen} onOpenChange={setIsDropoutDialogOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Registrar Desistência</DialogTitle>
              <DialogDescription>
                Registrar a desistência de {selectedAluno?.nome}
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label>Motivo da desistência *</Label>
                <Select
                  value={selectedDropoutReason}
                  onValueChange={setSelectedDropoutReason}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Selecione o motivo" />
                  </SelectTrigger>
                  <SelectContent>
                    {Array.isArray(dropoutReasons) && dropoutReasons.map((motivo) => (
                      <SelectItem key={motivo.id} value={motivo.id}>
                        {motivo.descricao}
                      </SelectItem>
                    ))}
                    <SelectItem value="outro">Outro</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              {selectedDropoutReason === "outro" && (
                <div>
                  <Label>Descreva o motivo *</Label>
                  <Textarea
                    value={dropoutReason}
                    onChange={(e) => setDropoutReason(e.target.value)}
                    placeholder="Descreva o motivo da desistência..."
                    rows={3}
                  />
                </div>
              )}
              <div className="flex justify-end space-x-2">
                <Button
                  variant="outline"
                  onClick={() => setIsDropoutDialogOpen(false)}
                >
                  Cancelar
                </Button>
                <Button
                  onClick={submitDropout}
                  className="bg-red-600 hover:bg-red-700"
                >
                  Registrar Desistência
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>

          {/* Dialog para solicitar reativação */}
          <Dialog open={isReativacaoDialogOpen} onOpenChange={setIsReativacaoDialogOpen}>
            <DialogContent className="max-w-md">
              <DialogHeader>
                <DialogTitle>Solicitar Reativação de Aluno</DialogTitle>
                <DialogDescription>
                  Solicitar reativação de {reativacaoAluno?.nome}. O administrador precisará aprovar.
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4">
                <div>
                  <Label>Motivo da reativação (opcional)</Label>
                  <Textarea
                    value={reativacaoMotivo}
                    onChange={(e) => setReativacaoMotivo(e.target.value)}
                    placeholder="Ex: Aluno resolveu os problemas que o levaram a desistir..."
                    rows={3}
                  />
                </div>
                <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <p className="text-sm text-yellow-800">
                    ⚠️ O administrador receberá essa solicitação e decidirá se aprova ou nega a reativação.
                  </p>
                </div>
                <div className="flex justify-end space-x-2">
                  <Button variant="outline" onClick={() => setIsReativacaoDialogOpen(false)} disabled={reativacaoSaving}>
                    Cancelar
                  </Button>
                  <Button onClick={submitReativacao} disabled={reativacaoSaving} className="bg-green-600 hover:bg-green-700">
                    {reativacaoSaving ? (
                      <span className="flex items-center gap-2">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                        Enviando...
                      </span>
                    ) : "📤 Enviar Solicitação"}
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
          {/* Dialog para upload de atestado */}
          <Dialog
          open={isAtestadoDialogOpen}
          onOpenChange={setIsAtestadoDialogOpen}
        >
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Upload Atestado Médico</DialogTitle>
              <DialogDescription>
                Enviar atestado médico para {selectedAluno?.nome}
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label>Arquivo do atestado *</Label>
                <Input
                  type="file"
                  accept=".pdf,.jpg,.jpeg,.png"
                  onChange={(e) => setSelectedFile(e.target.files[0])}
                />
                <p className="text-sm text-gray-500 mt-1">
                  Formatos aceitos: PDF, JPG, PNG (máx. 5MB)
                </p>
              </div>
              <div className="flex justify-end space-x-2">
                <Button
                  variant="outline"
                  onClick={() => setIsAtestadoDialogOpen(false)}
                >
                  Cancelar
                </Button>
                <Button
                  onClick={submitAtestado}
                  className="bg-green-600 hover:bg-green-700"
                >
                  <Upload className="h-4 w-4 mr-2" />
                  Enviar Atestado
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
  
        {/* 🚀 BULK UPLOAD DIALOG */}
        <Dialog open={isBulkUploadOpen} onOpenChange={setIsBulkUploadOpen}>
          <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>
                <Upload className="h-5 w-5 mr-2 inline" />
                Importação em Massa de Alunos
              </DialogTitle>
              <DialogDescription>
                Importe múltiplos alunos usando arquivo CSV.
                {user?.tipo === "admin"
                  ? " Você pode importar para qualquer curso."
                  : ` Você pode importar apenas para ${
                      user?.curso_nome || "seu curso"
                    }.`}
              </DialogDescription>
            </DialogHeader>
  
            <div className="space-y-6">
              {/* 📋 INSTRUÇÕES */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h3 className="font-semibold text-blue-800 mb-2">
                  📋 Formato do CSV
                </h3>
                <div className="text-sm text-blue-700 space-y-1">
                  <p>
                    <strong>Campos obrigatórios:</strong> nome_completo, cpf
                  </p>
                  <p>
                    <strong>Campos opcionais:</strong> nome_social
                  </p>
                  <p>
                    <strong>Formato CPF:</strong> Com ou sem pontuação (ex:
                    123.456.789-09 ou 12345678909)
                  </p>
                </div>
              </div>
  
              {/* 🎯 SELEÇÃO DE ARQUIVO */}
              <div className="space-y-4">
                <div>
                  <Label className="text-lg font-medium">
                    1. Selecione o arquivo CSV
                  </Label>
                  <div className="mt-2">
                    <Input
                      type="file"
                      accept=".csv"
                      onChange={(e) => setBulkUploadFile(e.target.files[0])}
                      className="border-2 border-dashed border-gray-300 p-4"
                    />
                    {bulkUploadFile && (
                      <p className="text-sm text-green-600 mt-2">
                        ✅ Arquivo selecionado: {bulkUploadFile.name}
                      </p>
                    )}
                  </div>
                </div>
  
                {/* 🎯 OPÇÕES DE IMPORTAÇÃO */}
                <div className="space-y-3">
                  <Label className="text-lg font-medium">
                    2. Opções de Importação
                  </Label>
  
                  {/* Atualizar existentes */}
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id="updateExisting"
                      checked={updateExisting}
                      onChange={(e) => setUpdateExisting(e.target.checked)}
                      className="rounded"
                    />
                    <label htmlFor="updateExisting" className="text-sm">
                      Atualizar alunos existentes (baseado no CPF)
                    </label>
                  </div>
  
                  {/* Seleção de turma padrão */}
                  {user?.tipo !== "monitor" && (
                    <div className="space-y-2">
                      <Label>Turma padrão (opcional)</Label>
                      <Select
                        value={selectedTurmaForBulk}
                        onValueChange={setSelectedTurmaForBulk}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Selecione uma turma padrão ou deixe em branco" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="sem_turma_padrao">
                            Sem turma padrão
                          </SelectItem>
                          {turmas
                            .filter(
                              (turma) =>
                                user?.tipo === "admin" ||
                                turma.curso_id === user?.curso_id,
                            )
                            .map((turma) => (
                              <SelectItem key={turma.id} value={turma.id}>
                                {turma.nome} -{" "}
                                {turma.curso_nome || "Curso não informado"}
                              </SelectItem>
                            ))}
                        </SelectContent>
                      </Select>
                      <p className="text-xs text-gray-500">
                        💡 Alunos sem turma especificada no CSV serão alocados
                        nesta turma
                      </p>
                    </div>
                  )}
                </div>
              </div>
  
              {/* 🎯 AÇÕES */}
              <div className="flex justify-between">
                <div className="space-x-2">
                  <Button
                    variant="outline"
                    onClick={downloadTemplate}
                    className="text-green-600 border-green-600 hover:bg-green-50"
                  >
                    <Download className="h-4 w-4 mr-2" />
                    Baixar Modelo CSV
                  </Button>
                </div>
  
                <div className="space-x-2">
                  <Button
                    variant="outline"
                    onClick={() => setIsBulkUploadOpen(false)}
                  >
                    Cancelar
                  </Button>
                  <Button
                    onClick={handleBulkUpload}
                    disabled={!bulkUploadFile || bulkUploading}
                    className="bg-green-600 hover:bg-green-700"
                  >
                    {bulkUploading ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Processando...
                      </>
                    ) : (
                      <>
                        <Upload className="h-4 w-4 mr-2" />
                        Importar Alunos
                      </>
                    )}
                  </Button>
                </div>
              </div>
            </div>
          </DialogContent>
        </Dialog>
  
        {/* 📊 BULK UPLOAD SUMMARY DIALOG */}
        <Dialog open={showBulkSummary} onOpenChange={setShowBulkSummary}>
          <DialogContent className="max-w-4xl max-h-[90vh]">
            <DialogHeader>
              <DialogTitle>📊 Resultado da Importação em Massa</DialogTitle>
              <DialogDescription>
                Resumo detalhado do processamento do arquivo CSV
              </DialogDescription>
            </DialogHeader>

            {bulkSummaryData && (
              <div className="space-y-6 overflow-y-auto max-h-[60vh]">

<div className="grid grid-cols-2 md:grid-cols-5 gap-3">
  
  <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-center">
    <div className="text-2xl font-bold text-green-700">
      {bulkSummaryData.summary?.inserted || 0}
    </div>
    <div className="text-sm text-green-600">✅ Inseridos</div>
  </div>

  {/* 👇 COMEÇO DA NOVA CAIXINHA DE ATUALIZADOS 👇 */}
  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-center">
    <div className="text-2xl font-bold text-blue-700">
      {bulkSummaryData.summary?.updated || 0}
    </div>
    <div className="text-sm text-blue-600">🔄 Atualizados</div>
  </div>
  {/* 👆 FIM DA NOVA CAIXINHA 👆 */}

  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-center">
    <div className="text-2xl font-bold text-yellow-700">
      {bulkSummaryData.summary?.skipped || 0}
    </div>
    <div className="text-sm text-yellow-600">⏭️ Pulados (duplicado)</div>
  </div>
      
                  <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-center">
                    <div className="text-2xl font-bold text-red-700">
                      {bulkSummaryData.summary?.errors_count || 0}
                    </div>
                    <div className="text-sm text-red-600">❌ Erros</div>
                  </div>
                  <div className="bg-orange-50 border border-orange-200 rounded-lg p-4 text-center">
                    <div className="text-2xl font-bold text-orange-700">
                      {bulkSummaryData.summary?.warnings_count || 0}
                    </div>
                    <div className="text-sm text-orange-600">⚠️ Avisos CPF</div>
                  </div>
                </div>

                {(bulkSummaryData.summary?.errors || []).length > 0 && (
                  <div>
                    <div className="flex justify-between items-center mb-2">
                      <h3 className="font-semibold text-red-700">
                        ❌ Erros ({bulkSummaryData.summary.errors.length})
                      </h3>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => downloadErrorReport(bulkSummaryData.summary.errors)}
                        className="text-red-600 border-red-600 hover:bg-red-50"
                      >
                        <Download className="h-4 w-4 mr-2" />
                        Baixar CSV de Erros
                      </Button>
                    </div>
                    <div className="max-h-48 overflow-y-auto rounded-lg border border-red-200">
                      <Table>
                        <TableHeader>
                          <TableRow className="bg-red-50">
                            <TableHead className="w-16">Linha</TableHead>
                            <TableHead>Nome do Aluno</TableHead>
                            <TableHead>Motivo</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {bulkSummaryData.summary.errors.map((erro, index) => (
                            <TableRow key={index}>
                              <TableCell className="font-mono text-sm text-gray-500">
                                {erro.line}
                              </TableCell>
                              <TableCell className="font-medium text-red-800">
                                {erro.data?.nome || erro.data?.cpf_original || "—"}
                              </TableCell>
                              <TableCell className="text-red-700 text-sm">
                                {erro.data?.motivo === "formato_invalido"
                                  ? `CPF inválido: "${erro.data.cpf_original}" — ${erro.data.digitos_encontrados} dígito(s), esperado 11`
                                  : erro.error?.substring(0, 150) || "Erro desconhecido"}
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </div>
                  </div>
                )}

                {(bulkSummaryData.summary?.warnings || []).length > 0 && (
                  <div>
                    <h3 className="font-semibold text-orange-700 mb-2">
                      ⚠️ Avisos de CPF ({bulkSummaryData.summary.warnings.length}) — alunos foram importados
                    </h3>
                    <div className="max-h-32 overflow-y-auto rounded-lg border border-orange-200">
                      <Table>
                        <TableHeader>
                          <TableRow className="bg-orange-50">
                            <TableHead className="w-16">Linha</TableHead>
                            <TableHead>Nome</TableHead>
                            <TableHead>CPF</TableHead>
                            <TableHead>Aviso</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {bulkSummaryData.summary.warnings.map((aviso, index) => (
                            <TableRow key={index}>
                              <TableCell className="font-mono text-sm text-gray-500">{aviso.line}</TableCell>
                              <TableCell className="font-medium">{aviso.data?.nome || "—"}</TableCell>
                              <TableCell className="font-mono text-sm">{aviso.data?.cpf_original || "—"}</TableCell>
                              <TableCell className="text-orange-700 text-sm">
                                Dígitos verificadores não conferem — verifique o documento
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </div>
                  </div>
                )}

                <div className="p-3 bg-gray-50 border rounded-lg text-sm text-gray-600">
                  <strong>Total processado:</strong> {bulkSummaryData.summary?.total_processed || 0} linhas
                  &nbsp;•&nbsp;
                  <strong>Taxa de sucesso:</strong> {bulkSummaryData.summary?.success_rate || "0%"}
                </div>

              </div>
            )}

            <div className="flex justify-end space-x-2 mt-4">
              <Button variant="outline" onClick={() => setShowBulkSummary(false)}>
                Fechar
              </Button>
              <Button
                onClick={() => {
                  setShowBulkSummary(false);
                  fetchAlunos();
                }}
                className="bg-blue-600 hover:bg-blue-700"
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Atualizar Lista
              </Button>
            </div>
          </DialogContent>
        </Dialog>  
  
        {/* Dialog de visualização detalhada do aluno */}
        <Dialog
          open={isViewAlunoDialogOpen}
          onOpenChange={setIsViewAlunoDialogOpen}
        >
          <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle className="flex items-center">
                <Users className="h-5 w-5 mr-2" />
                Perfil Completo - {viewingAluno?.nome}
              </DialogTitle>
              <DialogDescription>
                Visualize informações detalhadas e justificativas do aluno
              </DialogDescription>
            </DialogHeader>
  
            {viewingAluno && (
            <Tabs defaultValue="dados" className="w-full">
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger value="dados">Dados Pessoais</TabsTrigger>
                <TabsTrigger value="turma">Turma e Curso</TabsTrigger>
                <TabsTrigger value="justificativas">
                  Justificativas ({studentJustifications.length})
                </TabsTrigger>
                <TabsTrigger value="frequencia">Frequência</TabsTrigger>
              </TabsList>
                {/* Aba de Dados Pessoais */}
                <TabsContent value="dados" className="space-y-4 mt-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Dados Obrigatórios */}
                    <Card>
                      <CardHeader>
                        <CardTitle className="text-lg flex items-center">
                          <UserCheck className="h-5 w-5 mr-2" />
                          Dados Obrigatórios
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-3">
                        <div>
                          <Label className="text-sm font-medium text-gray-600">
                            Nome Completo
                          </Label>
                          <p className="text-base font-medium">
                            {viewingAluno.nome}
                          </p>
                        </div>
                        <div>
                          <Label className="text-sm font-medium text-gray-600">
                            CPF
                          </Label>
                          <p className="text-base font-mono">
                            {viewingAluno.cpf}
                          </p>
                        </div>
                        <div>
                          <Label className="text-sm font-medium text-gray-600">
                            Idade
                          </Label>
                          <p className="text-base">
                            {viewingAluno.idade
                              ? `${viewingAluno.idade} anos`
                              : "N/A"}
                          </p>
                        </div>
                        <div>
                          <Label className="text-sm font-medium text-gray-600">
                            Data de Nascimento
                          </Label>
                          <p className="text-base">
                            {viewingAluno.data_nascimento || "N/A"}
                          </p>
                        </div>
                      </CardContent>
                    </Card>
  
                    {/* Dados Complementares */}
                    <Card>
                      <CardHeader>
                        <CardTitle className="text-lg flex items-center">
                          <BookOpen className="h-5 w-5 mr-2" />
                          Dados Complementares
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-3">
                        <div>
                          <Label className="text-sm font-medium text-gray-600">
                            RG
                          </Label>
                          <p className="text-base">{viewingAluno.rg || "N/A"}</p>
                        </div>
                        <div>
                          <Label className="text-sm font-medium text-gray-600">
                            Gênero
                          </Label>
                          <p className="text-base">
                            {viewingAluno.genero || "N/A"}
                          </p>
                        </div>
                        <div>
                          <Label className="text-sm font-medium text-gray-600">
                            Telefone
                          </Label>
                          <p className="text-base">
                            {viewingAluno.telefone || "N/A"}
                          </p>
                        </div>
                        <div>
                          <Label className="text-sm font-medium text-gray-600">
                            Email
                          </Label>
                          <p className="text-base">
                            {viewingAluno.email || "N/A"}
                          </p>
                        </div>
                      </CardContent>
                    </Card>
  
                    {/* Dados do Responsável */}
                    <Card>
                      <CardHeader>
                        <CardTitle className="text-lg flex items-center">
                          <Users className="h-5 w-5 mr-2" />
                          Dados do Responsável
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-3">
                        <div>
                          <Label className="text-sm font-medium text-gray-600">
                            Nome do Responsável
                          </Label>
                          <p className="text-base">
                            {viewingAluno.nome_responsavel || "N/A"}
                          </p>
                        </div>
                        <div>
                          <Label className="text-sm font-medium text-gray-600">
                            Telefone do Responsável
                          </Label>
                          <p className="text-base">
                            {viewingAluno.telefone_responsavel || "N/A"}
                          </p>
                        </div>
                      </CardContent>
                    </Card>
  
                    {/* Endereço e Observações */}
                    <Card>
                      <CardHeader>
                        <CardTitle className="text-lg flex items-center">
                          <Building2 className="h-5 w-5 mr-2" />
                          Outras Informações
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-3">
                        <div>
                          <Label className="text-sm font-medium text-gray-600">
                            Endereço
                          </Label>
                          <p className="text-base">
                            {viewingAluno.endereco || "N/A"}
                          </p>
                        </div>
                        <div>
                          <Label className="text-sm font-medium text-gray-600">
                            Observações
                          </Label>
                          <p className="text-base">
                            {viewingAluno.observacoes || "N/A"}
                          </p>
                        </div>
                        <div>
                          <Label className="text-sm font-medium text-gray-600">
                            Status
                          </Label>
                          <Badge variant={getStatusColor(viewingAluno.status)}>
                            {getStatusLabel(viewingAluno.status)}
                          </Badge>
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                </TabsContent>


                         {/* Aba Turma e Curso */}
                <TabsContent value="turma" className="space-y-4 mt-4">
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center">
                        <GraduationCap className="h-5 w-5 mr-2" />
                        Turma e Curso
                      </CardTitle>
                      <CardDescription>
                        Veja a turma atual do aluno ou transfira para outra
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <TransferirTurmaPanel
                        aluno={viewingAluno}
                        turmas={turmas}
                        onTransferido={() => {
                          fetchTurmas();
                          fetchAlunos();
                        }}
                      />
                    </CardContent>
                  </Card>
                </TabsContent>
                
                {/* Aba Frequência */}
                <TabsContent value="frequencia" className="space-y-4 mt-4">
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center">
                        <BarChart3 className="h-5 w-5 mr-2" />
                        Frequência
                      </CardTitle>
                      <CardDescription>
                        Dados de presença e faltas deste aluno
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <FrequenciaAlunoPanel alunoId={viewingAluno?.id} />
                    </CardContent>
                  </Card>
                </TabsContent>
                {/* Aba de Justificativas */}
                <TabsContent value="justificativas" className="space-y-4 mt-4">
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center">
                        <FileText className="h-5 w-5 mr-2" />
                        Histórico de Justificativas
                      </CardTitle>
                      <CardDescription>
                        Justificativas de faltas registradas para este aluno
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      {loadingJustifications ? (
                        <div className="text-center py-8">
                          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                          <p className="text-sm text-gray-500 mt-2">
                            Carregando justificativas...
                          </p>
                        </div>
                      ) : studentJustifications.length === 0 ? (
                        <div className="text-center py-8 text-gray-500">
                          <FileText className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                          <p>Nenhuma justificativa registrada</p>
                          <p className="text-sm">
                            Este aluno não possui justificativas de faltas
                          </p>
                        </div>
                      ) : (
                        <div className="space-y-4">
                    {Array.isArray(studentJustifications) &&
                      studentJustifications.map((justification) => (
                        <Card
                          key={justification.id}
                          className="border-l-4 border-l-blue-500"
                        >
                          <CardContent className="pt-4">
                            <div className="flex justify-between items-start">
                              <div className="flex-1">
                                <div className="flex items-center space-x-2 mb-2">
                                  <Badge variant="outline">
                                    {justification.reason_text || justification.reason_code || "Justificativa"}
                                  </Badge>
                                  <span className="text-sm text-gray-500">
                                    {justification.uploaded_at
                                      ? new Date(justification.uploaded_at).toLocaleDateString("pt-BR")
                                      : ""}
                                  </span>
                                </div>
                    
                                {justification.reason_text && (
                                  <div className="mb-3">
                                    <Label className="text-sm font-medium text-gray-600">
                                      Observações:
                                    </Label>
                                    <p className="text-sm bg-gray-50 p-2 rounded border">
                                      {justification.reason_text}
                                    </p>
                                  </div>
                                )}
                    
                                <div className="text-xs text-gray-500">
                                  Registrado por: {justification.uploaded_by_name || "—"}
                                </div>
                    
                                {justification.attendance_id && (
                                  <div className="text-xs text-gray-500">
                                    Vinculada à chamada: {justification.attendance_id}
                                  </div>
                                )}
                              </div>
                    
                              <div className="flex space-x-2 ml-4">
                                {justification.has_file && (
                                  <Button
                                    onClick={() =>
                                      downloadJustificationFile(
                                        justification.id,
                                        justification.file_name,
                                      )
                                    }
                                    variant="outline"
                                    size="sm"
                                    title="Baixar documento"
                                  >
                                    <Download className="h-4 w-4" />
                                  </Button>
                                )}
                    
                                <Button
                                  onClick={() =>
                                    deleteJustification(justification.id)
                                  }
                                  variant="outline"
                                  size="sm"
                                  className="text-red-600 border-red-600 hover:bg-red-50"
                                  title="Remover justificativa"
                                >
                                  <Trash2 className="h-4 w-4" />
                                </Button>
                              </div>
                            </div>
                          </CardContent>
                        </Card>
))}
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </TabsContent>

              </Tabs>
            )}

            <div className="flex justify-end pt-4">
              <Button
                variant="outline"
                onClick={() => setIsViewAlunoDialogOpen(false)}
              >
                Fechar
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </Card>
    );
  };
  
  // Unidades Manager Component COMPLETO
  const UnidadesManager = () => {
  const [unidades, setUnidades] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isDialogOpen, setIsDialogOpen] = useState(false);  // ← FALTAVA
  const [editingUnidade, setEditingUnidade] = useState(null);
  const [formData, setFormData] = useState({
    nome: "",
    endereco: "",
    telefone: "",
    responsavel: "",
    email: "",
  });
  const { toast } = useToast();  // ← FALTAVA
  
  
    useEffect(() => {
      fetchUnidades();
    }, []);
  
    const fetchUnidades = async () => {
      try {
        const response = await axios.get(`${API}/units`);
        setUnidades(response.data);
      } catch (error) {
        console.error("Error fetching unidades:", error);
      } finally {
        setLoading(false);
      }
    };
  
    const handleSubmit = async (e) => {
      e.preventDefault();
      try {
        if (editingUnidade) {
          await axios.put(`${API}/units/${editingUnidade.id}`, formData);
          toast({
            title: "Unidade atualizada com sucesso!",
            description: "As informações da unidade foram atualizadas.",
          });
        } else {
          await axios.post(`${API}/units`, formData);
          toast({
            title: "Unidade criada com sucesso!",
            description: "A nova unidade foi adicionada ao sistema.",
          });
        }
  
        setIsDialogOpen(false);
        setEditingUnidade(null);
        resetForm();
        fetchUnidades();
      } catch (error) {
        toast({
          title: editingUnidade
            ? "Erro ao atualizar unidade"
            : "Erro ao criar unidade",
          description: error.response?.data?.detail || "Tente novamente",
          variant: "destructive",
        });
      }
    };
  
    const resetForm = () => {
      setFormData({
        nome: "",
        endereco: "",
        telefone: "",
        responsavel: "",
        email: "",
      });
    };
  
    const handleEdit = (unidade) => {
      setEditingUnidade(unidade);
      setFormData({
        nome: unidade.nome,
        endereco: unidade.endereco,
        telefone: unidade.telefone || "",
        responsavel: unidade.responsavel || "",
        email: unidade.email || "",
      });
      setIsDialogOpen(true);
    };
  
    const handleDelete = async (unidadeId) => {
      if (window.confirm("Tem certeza que deseja desativar esta unidade?")) {
        try {
          await axios.delete(`${API}/units/${unidadeId}`);
          toast({
            title: "Unidade desativada com sucesso!",
            description: "A unidade foi desativada do sistema.",
          });
          fetchUnidades();
        } catch (error) {
          toast({
            title: "Erro ao desativar unidade",
            description: error.response?.data?.detail || "Tente novamente",
            variant: "destructive",
          });
        }
      }
    };
  
    const handleOpenDialog = () => {
      setEditingUnidade(null);
      resetForm();
      setIsDialogOpen(true);
    };
  
    if (loading)
      return (
        <div key="unidades-loading" className="p-8 text-center">
          Carregando unidades...
        </div>
      );
  
    return (
      <Card key="unidades-content">
        <CardHeader>
          <div className="flex justify-between items-center">
            <div>
              <CardTitle>Gerenciamento de Unidades</CardTitle>
              <CardDescription>
                Gerencie as unidades do Instituto da Oportunidade Social
              </CardDescription>
            </div>
            <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
              <DialogTrigger asChild>
                <Button
                  onClick={handleOpenDialog}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Nova Unidade
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-md">
                <DialogHeader>
                  <DialogTitle>
                    {editingUnidade ? "Editar Unidade" : "Criar Nova Unidade"}
                  </DialogTitle>
                  <DialogDescription>
                    {editingUnidade
                      ? "Atualize os dados da unidade"
                      : "Preencha os dados para criar uma nova unidade"}
                  </DialogDescription>
                </DialogHeader>
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="nome">Nome da Unidade</Label>
                    <Input
                      id="nome"
                      value={formData.nome}
                      onChange={(e) =>
                        setFormData({ ...formData, nome: e.target.value })
                      }
                      placeholder="Ex: Unidade Centro"
                      required
                    />
                  </div>
  
                  <div className="space-y-2">
                    <Label htmlFor="endereco">Endereço</Label>
                    <Input
                      id="endereco"
                      value={formData.endereco}
                      onChange={(e) =>
                        setFormData({ ...formData, endereco: e.target.value })
                      }
                      placeholder="Rua, número, bairro, cidade"
                      required
                    />
                  </div>
  
                  <div className="space-y-2">
                    <Label htmlFor="telefone">Telefone</Label>
                    <Input
                      id="telefone"
                      value={formData.telefone}
                      onChange={(e) =>
                        setFormData({ ...formData, telefone: e.target.value })
                      }
                      placeholder="(11) 1234-5678"
                    />
                  </div>
  
                  <div className="space-y-2">
                    <Label htmlFor="responsavel">Responsável</Label>
                    <Input
                      id="responsavel"
                      value={formData.responsavel}
                      onChange={(e) =>
                        setFormData({ ...formData, responsavel: e.target.value })
                      }
                      placeholder="Nome do responsável"
                    />
                  </div>
  
                  <div className="space-y-2">
                    <Label htmlFor="email">Email</Label>
                    <Input
                      id="email"
                      type="email"
                      value={formData.email}
                      onChange={(e) =>
                        setFormData({ ...formData, email: e.target.value })
                      }
                      placeholder="unidade@ios.com.br"
                    />
                  </div>
  
                  <Button
                    type="submit"
                    className="w-full bg-blue-600 hover:bg-blue-700"
                  >
                    <Save className="h-4 w-4 mr-2" />
                    {editingUnidade ? "Atualizar Unidade" : "Criar Unidade"}
                  </Button>
                </form>
              </DialogContent>
            </Dialog>
          </div>
        </CardHeader>
        <CardContent>
                      
          <div className="table-container">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Nome</TableHead>
                  <TableHead>Endereço</TableHead>
                  <TableHead>Contato</TableHead>
                  <TableHead>Responsável</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Ações</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {Array.isArray(unidades) &&
                  unidades.map((unidade) => (
                    <TableRow key={unidade.id}>
                      <TableCell className="font-medium">
                        {unidade.nome}
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center">
                          <MapPin className="h-4 w-4 mr-1 text-gray-400" />
                          {unidade.endereco}
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="space-y-1">
                          {unidade.telefone && (
                            <div className="flex items-center text-sm">
                              <Phone className="h-3 w-3 mr-1 text-gray-400" />
                              {unidade.telefone}
                            </div>
                          )}
                          {unidade.email && (
                            <div className="flex items-center text-sm">
                              <Mail className="h-3 w-3 mr-1 text-gray-400" />
                              {unidade.email}
                            </div>
                          )}
                        </div>
                      </TableCell>
                      <TableCell>{unidade.responsavel || "-"}</TableCell>
                      <TableCell>
                        <Badge variant={unidade.ativo ? "default" : "secondary"}>
                          {unidade.ativo ? "Ativa" : "Inativa"}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex space-x-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleEdit(unidade)}
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleDelete(unidade.id)}
                            className="text-red-600 hover:text-red-700"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    );
  };
  
  // Cursos Manager Component COMPLETO
  const CursosManager = () => {
    const [cursos, setCursos] = useState([]);
    const [loading, setLoading] = useState(true);
    const [isDialogOpen, setIsDialogOpen] = useState(false);
    const [editingCurso, setEditingCurso] = useState(null);
    const [formData, setFormData] = useState({
      nome: "",
      descricao: "",
      carga_horaria: "",
      categoria: "",
      pre_requisitos: "",
      dias_aula: ["segunda", "terca", "quarta", "quinta"], // 📅 Dias de aula padrão
    });
    const { toast } = useToast();
  
    useEffect(() => {
      fetchCursos();
    }, []);
  
    const fetchCursos = async () => {
      try {
        const response = await axios.get(`${API}/courses`);
        setCursos(response.data);
      } catch (error) {
        console.error("Error fetching cursos:", error);
      } finally {
        setLoading(false);
      }
    };
  
    const handleSubmit = async (e) => {
      e.preventDefault();
      try {
        const submitData = {
          ...formData,
          carga_horaria: parseInt(formData.carga_horaria),
        };
  
        if (editingCurso) {
          await axios.put(`${API}/courses/${editingCurso.id}`, submitData);
          toast({
            title: "Curso atualizado com sucesso!",
            description: "As informações do curso foram atualizadas.",
          });
        } else {
          await axios.post(`${API}/courses`, submitData);
          toast({
            title: "Curso criado com sucesso!",
            description: "O novo curso foi adicionado ao sistema.",
          });
        }
  
        setIsDialogOpen(false);
        setEditingCurso(null);
        resetForm();
        fetchCursos();
      } catch (error) {
        toast({
          title: editingCurso ? "Erro ao atualizar curso" : "Erro ao criar curso",
          description: error.response?.data?.detail || "Tente novamente",
          variant: "destructive",
        });
      }
    };
  
    const resetForm = () => {
      setFormData({
        nome: "",
        descricao: "",
        carga_horaria: "",
        categoria: "",
        pre_requisitos: "",
        dias_aula: ["segunda", "terca", "quarta", "quinta"], // 📅 Resetar dias padrão
      });
    };
  
    const handleEdit = (curso) => {
      setEditingCurso(curso);
      setFormData({
        nome: curso.nome,
        descricao: curso.descricao || "",
        carga_horaria: curso.carga_horaria.toString(),
        categoria: curso.categoria || "",
        pre_requisitos: curso.pre_requisitos || "",
        dias_aula: curso.dias_aula || ["segunda", "terca", "quarta", "quinta"], // 📅 Carregar dias de aula
      });
      setIsDialogOpen(true);
    };
  
    const handleDelete = async (cursoId) => {
      if (window.confirm("Tem certeza que deseja desativar este curso?")) {
        try {
          await axios.delete(`${API}/courses/${cursoId}`);
          toast({
            title: "Curso desativado com sucesso!",
            description: "O curso foi desativado do sistema.",
          });
          fetchCursos();
        } catch (error) {
          toast({
            title: "Erro ao desativar curso",
            description: error.response?.data?.detail || "Tente novamente",
            variant: "destructive",
          });
        }
      }
    };
  
    const handleOpenDialog = () => {
      setEditingCurso(null);
      resetForm();
      setIsDialogOpen(true);
    };
  
    if (loading)
      return (
        <div key="cursos-loading" className="p-8 text-center">
          Carregando cursos...
        </div>
      );
  
    return (
      <Card key="cursos-content">
        <CardHeader>
          <div className="flex justify-between items-center">
            <div>
              <CardTitle>Gerenciamento de Cursos</CardTitle>
              <CardDescription>
                Gerencie os cursos oferecidos pelo Instituto
              </CardDescription>
            </div>
            <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
              <DialogTrigger asChild>
                <Button
                  onClick={handleOpenDialog}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Novo Curso
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-md">
                <DialogHeader>
                  <DialogTitle>
                    {editingCurso ? "Editar Curso" : "Criar Novo Curso"}
                  </DialogTitle>
                  <DialogDescription>
                    {editingCurso
                      ? "Atualize os dados do curso"
                      : "Preencha os dados para criar um novo curso"}
                  </DialogDescription>
                </DialogHeader>
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="nome">Nome do Curso</Label>
                    <Input
                      id="nome"
                      value={formData.nome}
                      onChange={(e) =>
                        setFormData({ ...formData, nome: e.target.value })
                      }
                      placeholder="Ex: Informática Básica"
                      required
                    />
                  </div>
  
                  <div className="space-y-2">
                    <Label htmlFor="descricao">Descrição</Label>
                    <Textarea
                      id="descricao"
                      value={formData.descricao}
                      onChange={(e) =>
                        setFormData({ ...formData, descricao: e.target.value })
                      }
                      placeholder="Descreva o curso..."
                    />
                  </div>
  
                  <div className="space-y-2">
                    <Label htmlFor="carga_horaria">Carga Horária (horas)</Label>
                    <Input
                      id="carga_horaria"
                      type="number"
                      value={formData.carga_horaria}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          carga_horaria: e.target.value,
                        })
                      }
                      placeholder="Ex: 80"
                      min="1"
                      required
                    />
                  </div>
  
                  {/* 📅 Campo Dias de Aula */}
                  <div className="space-y-2">
                    <Label>Dias de Aula</Label>
                    <div className="grid grid-cols-2 gap-3">
                      {[
                        { key: "segunda", label: "Segunda" },
                        { key: "terca", label: "Terça" },
                        { key: "quarta", label: "Quarta" },
                        { key: "quinta", label: "Quinta" },
                        { key: "sexta", label: "Sexta" },
                        { key: "sabado", label: "Sábado" },
                      ].map((dia) => (
                        <div
                          key={dia.key}
                          className="flex items-center space-x-2"
                        >
                          <Checkbox
                            id={dia.key}
                            checked={formData.dias_aula.includes(dia.key)}
                            onCheckedChange={(checked) => {
                              if (checked) {
                                setFormData({
                                  ...formData,
                                  dias_aula: [...formData.dias_aula, dia.key],
                                });
                              } else {
                                setFormData({
                                  ...formData,
                                  dias_aula: formData.dias_aula.filter(
                                    (d) => d !== dia.key,
                                  ),
                                });
                              }
                            }}
                          />
                          <Label
                            htmlFor={dia.key}
                            className="text-sm font-normal cursor-pointer"
                          >
                            {dia.label}
                          </Label>
                        </div>
                      ))}
                    </div>
                    <p className="text-xs text-gray-500">
                      Selecione os dias da semana em que o curso tem aulas
                    </p>
                  </div>
  
                  <div className="space-y-2">
                    <Label htmlFor="categoria">Categoria</Label>
                    <Input
                      id="categoria"
                      value={formData.categoria}
                      onChange={(e) =>
                        setFormData({ ...formData, categoria: e.target.value })
                      }
                      placeholder="Ex: Tecnologia, Gestão"
                    />
                  </div>
  
                  <div className="space-y-2">
                    <Label htmlFor="pre_requisitos">Pré-requisitos</Label>
                    <Textarea
                      id="pre_requisitos"
                      value={formData.pre_requisitos}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          pre_requisitos: e.target.value,
                        })
                      }
                      placeholder="Liste os pré-requisitos..."
                    />
                  </div>
  
                  <Button
                    type="submit"
                    className="w-full bg-blue-600 hover:bg-blue-700"
                  >
                    <Save className="h-4 w-4 mr-2" />
                    {editingCurso ? "Atualizar Curso" : "Criar Curso"}
                  </Button>
                </form>
              </DialogContent>
            </Dialog>
          </div>
        </CardHeader>
        <CardContent>
          <div className="table-container">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Nome</TableHead>
                  <TableHead>Categoria</TableHead>
                  <TableHead>Carga Horária</TableHead>
                  <TableHead>Descrição</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Ações</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {Array.isArray(cursos) &&
                  cursos.map((curso) => (
                    <TableRow key={curso.id}>
                      <TableCell className="font-medium">{curso.nome}</TableCell>
                      <TableCell>
                        {curso.categoria && (
                          <Badge variant="outline">{curso.categoria}</Badge>
                        )}
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center">
                          <Clock className="h-4 w-4 mr-1 text-gray-400" />
                          {curso.carga_horaria}h
                        </div>
                      </TableCell>
                      <TableCell className="max-w-xs truncate">
                        {curso.descricao || "-"}
                      </TableCell>
                      <TableCell>
                        <Badge variant={curso.ativo ? "default" : "secondary"}>
                          {curso.ativo ? "Ativo" : "Inativo"}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex space-x-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleEdit(curso)}
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleDelete(curso.id)}
                            className="text-red-600 hover:text-red-700"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    );
  };
  
  // Main App Component
  function App() {
    return (
      <ErrorBoundary>
        <AuthProvider>
          <div className="App">
            <BrowserRouter>
              <Routes>
                <Route path="/login" element={<LoginRoute />} />
                <Route
                  path="/"
                  element={
                    <ProtectedRoute>
                      <Dashboard />
                    </ProtectedRoute>
                  }
                />
              </Routes>
            </BrowserRouter>
            <Toaster />
          </div>
        </AuthProvider>
      </ErrorBoundary>
    );
  }
  
  // Route Components
  const LoginRoute = () => {
    const { user, loading } = useAuth();
  
    if (loading)
      return (
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-purple-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Carregando IOS...</p>
            <p className="text-sm text-gray-400 mt-2">
              Se demorar muito, recarregue a página
            </p>
          </div>
        </div>
      );
    if (user) return <Navigate to="/" replace />;
  
    return <Login />;
  };
  
    const ProtectedRoute = ({ children }) => {
      const { user, setUser, loading } = useAuth();
  
    if (loading)
      return (
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-purple-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Verificando autenticação...</p>
          </div>
        </div>
      );
    if (!user) return <Navigate to="/login" replace />;

  // 🔐 PRIMEIRO ACESSO: Redirecionar para troca de senha obrigatória
  if (user?.primeiro_acesso === true || user?.primeiro_acesso === 1 || user?.primeiro_acesso === "true") {
    return (
      <PrimeiroAcessoPage
        onSenhaAlterada={() => {
          setUser((prev) => ({ ...prev, primeiro_acesso: false }));
        }}
      />
    );
  }

return children;
};

export default App;
