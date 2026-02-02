#!/usr/bin/env python3
"""
VERIFICAÇÃO FINAL - Testar funcionalidade completa de 2 instrutores
"""

import requests
import json

BACKEND_URL = "https://sistema-ios-backend.onrender.com/api"

def test_complete():
    print("=" * 80)
    print("TESTE FINAL: Funcionalidade de 2 Instrutores")
    print("=" * 80)
    
    # Login admin
    resp = requests.post(f"{BACKEND_URL}/auth/login", 
                        json={"email": "jesiel.junior@ios.org.br", "senha": "b99018cd"})
    if resp.status_code != 200:
        print(f"❌ Login falhou: {resp.status_code}")
        return
    
    token = resp.json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login admin OK")
    
    # Buscar recursos
    unidades = requests.get(f"{BACKEND_URL}/units", headers=headers).json()
    cursos = requests.get(f"{BACKEND_URL}/courses", headers=headers).json()
    usuarios = requests.get(f"{BACKEND_URL}/users", headers=headers).json()
    instrutores = [u for u in usuarios if u.get('tipo') == 'instrutor'][:2]  # Pegar 2 instrutores
    
    if len(instrutores) < 2:
        print(f"❌ Precisa de pelo menos 2 instrutores. Encontrados: {len(instrutores)}")
        return
    
    print(f"✅ Recursos carregados:")
    print(f"   Unidade: {unidades[0]['nome']}")
    print(f"   Curso: {cursos[0]['nome']}")
    print(f"   Instrutor 1: {instrutores[0]['nome']}")
    print(f"   Instrutor 2: {instrutores[1]['nome']}")
    
    # TESTE 1: Criar turma com 2 instrutores
    print("\n" + "=" * 80)
    print("TESTE 1: Criar turma com 2 instrutores")
    print("=" * 80)
    
    turma_data = {
        "nome": "TESTE 2 INSTRUTORES - DELETAR",
        "unidade_id": unidades[0]['id'],
        "curso_id": cursos[0]['id'],
        "instrutor_id": instrutores[0]['id'],  # COMPATIBILIDADE: Envia formato antigo também
        "instrutor_ids": [instrutores[0]['id'], instrutores[1]['id']],  # 2 INSTRUTORES
        "data_inicio": "2025-03-01",
        "data_fim": "2025-12-15",
        "horario_inicio": "08:00",
        "horario_fim": "12:00",
        "dias_semana": ["segunda", "terca"],
        "vagas_total": 30,
        "ciclo": "01/2025",
        "tipo_turma": "regular"
    }
    
    resp = requests.post(f"{BACKEND_URL}/classes", json=turma_data, headers=headers)
    
    if resp.status_code == 200:
        turma = resp.json()
        turma_id = turma['id']
        print(f"✅ Turma criada com sucesso!")
        print(f"   ID: {turma_id}")
        print(f"   instrutor_ids: {turma.get('instrutor_ids')}")
        
        if 'instrutor_id' in turma:
            print(f"   ⚠️ ATENÇÃO: Campo antigo 'instrutor_id' ainda presente: {turma['instrutor_id']}")
        
        # TESTE 2: Verificar se ambos instrutores veem a turma
        print("\n" + "=" * 80)
        print("TESTE 2: Verificar visibilidade para ambos instrutores")
        print("=" * 80)
        
        for i, instrutor in enumerate(instrutores[:2], 1):
            # Login como instrutor (senha padrão IOS)
            resp_login = requests.post(f"{BACKEND_URL}/auth/login",
                                      json={"email": instrutor['email'], "senha": "b99018cd"})
            
            if resp_login.status_code != 200:
                print(f"❌ Instrutor {i} ({instrutor['nome']}): Login falhou")
                continue
            
            instrutor_token = resp_login.json()['access_token']
            instrutor_headers = {"Authorization": f"Bearer {instrutor_token}"}
            
            # Buscar turmas do instrutor
            turmas_resp = requests.get(f"{BACKEND_URL}/classes", headers=instrutor_headers)
            turmas = turmas_resp.json()
            
            turma_encontrada = any(t['id'] == turma_id for t in turmas)
            
            if turma_encontrada:
                print(f"✅ Instrutor {i} ({instrutor['nome']}): VÊ a turma")
            else:
                print(f"❌ Instrutor {i} ({instrutor['nome']}): NÃO vê a turma")
        
        # Deletar turma de teste
        print("\n" + "=" * 80)
        print("Limpeza")
        print("=" * 80)
        resp_del = requests.delete(f"{BACKEND_URL}/classes/{turma_id}", headers=headers)
        if resp_del.status_code == 200:
            print("✅ Turma de teste deletada")
        
        print("\n" + "=" * 80)
        print("🎉 TESTE COMPLETO!")
        print("=" * 80)
        
    elif resp.status_code == 422:
        error = resp.json()
        print(f"❌ ERRO 422 - Backend ainda usa modelo antigo:")
        print(json.dumps(error, indent=2))
        print("\n⚠️ Aguarde mais alguns minutos e execute novamente")
    else:
        print(f"❌ Erro {resp.status_code}: {resp.text}")

if __name__ == "__main__":
    test_complete()
