#!/usr/bin/env python3
"""
Aguardar deploy do Render e testar novo código
"""

import requests
import time
import json

BACKEND_URL = "https://sistema-ios-backend.onrender.com/api"

def check_deploy():
    """Verifica se deploy está pronto com novo código"""
    
    print("🔍 Verificando versão do backend no Render...")
    print("=" * 80)
    
    for tentativa in range(1, 31):  # 30 tentativas = ~15 minutos
        try:
            # Tentar login
            resp = requests.post(
                f"{BACKEND_URL}/auth/login",
                json={"email": "jesiel.junior@ios.org.br", "senha": "b99018cd"},
                timeout=10
            )
            
            if resp.status_code == 200:
                token = resp.json()['access_token']
                headers = {"Authorization": f"Bearer {token}"}
                
                # Buscar unidade, curso e instrutor
                unidades = requests.get(f"{BACKEND_URL}/units", headers=headers).json()
                cursos = requests.get(f"{BACKEND_URL}/courses", headers=headers).json()
                usuarios = requests.get(f"{BACKEND_URL}/users", headers=headers).json()
                instrutores = [u for u in usuarios if u.get('tipo') == 'instrutor']
                
                # Tentar criar turma com instrutor_ids
                turma_data = {
                    "nome": "TESTE DEPLOY",
                    "unidade_id": unidades[0]['id'],
                    "curso_id": cursos[0]['id'],
                    "instrutor_ids": [instrutores[0]['id']],  # NOVO CAMPO
                    "data_inicio": "2025-03-01",
                    "data_fim": "2025-12-15",
                    "horario_inicio": "08:00",
                    "horario_fim": "12:00",
                    "dias_semana": ["segunda"],
                    "vagas_total": 30,
                    "ciclo": "01/2025",
                    "tipo_turma": "regular"
                }
                
                create_resp = requests.post(
                    f"{BACKEND_URL}/classes",
                    json=turma_data,
                    headers=headers,
                    timeout=10
                )
                
                if create_resp.status_code == 200:
                    print(f"\n🎉 DEPLOY CONCLUÍDO! (Tentativa {tentativa})")
                    print("✅ Backend aceita 'instrutor_ids'")
                    
                    # Deletar turma de teste
                    turma_id = create_resp.json()['id']
                    requests.delete(f"{BACKEND_URL}/classes/{turma_id}", headers=headers)
                    print("✅ Turma de teste removida")
                    
                    print("\n✨ Agora você pode criar turmas com 2 instrutores!")
                    return True
                    
                elif create_resp.status_code == 422:
                    error_detail = create_resp.json().get('detail', [])
                    missing_field = None
                    if error_detail:
                        for err in error_detail:
                            if err.get('type') == 'missing':
                                missing_field = err.get('loc', [])[1] if len(err.get('loc', [])) > 1 else None
                    
                    if missing_field == 'instrutor_id':
                        print(f"⏳ Tentativa {tentativa}/30: Ainda na versão antiga (requer instrutor_id)")
                    else:
                        print(f"⚠️ Tentativa {tentativa}/30: Erro 422: {error_detail}")
                else:
                    print(f"⚠️ Tentativa {tentativa}/30: Status {create_resp.status_code}")
            else:
                print(f"⚠️ Tentativa {tentativa}/30: Login falhou ({resp.status_code})")
                
        except requests.exceptions.Timeout:
            print(f"⏳ Tentativa {tentativa}/30: Timeout (servidor reiniciando)")
        except requests.exceptions.ConnectionError:
            print(f"⏳ Tentativa {tentativa}/30: Conexão falhou (servidor offline)")
        except Exception as e:
            print(f"❌ Tentativa {tentativa}/30: Erro: {str(e)}")
        
        if tentativa < 30:
            time.sleep(30)  # Aguardar 30 segundos
    
    print("\n❌ Deploy não completou em 15 minutos")
    print("Verifique manualmente: https://dashboard.render.com")
    return False

if __name__ == "__main__":
    check_deploy()
