#!/usr/bin/env python3
"""
Buscar turma Teste via API do Render em produção
"""

import requests

BACKEND_URL = "https://sistema-ios-backend.onrender.com/api"

def buscar_turma_teste():
    # Login admin
    resp = requests.post(f"{BACKEND_URL}/auth/login", 
                        json={"email": "jesiel.junior@ios.org.br", "senha": "b99018cd"})
    token = resp.json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    
    # Buscar todas as turmas
    print("Buscando turmas via Render API...")
    resp = requests.get(f"{BACKEND_URL}/classes", headers=headers)
    turmas = resp.json()
    
    # Encontrar turma Teste
    turma_teste = None
    for t in turmas:
        if t.get('nome') == 'Teste':
            turma_teste = t
            break
    
    if turma_teste:
        print("\n" + "=" * 80)
        print("TURMA 'Teste' ENCONTRADA NO RENDER!")
        print("=" * 80)
        print(f"ID: {turma_teste.get('id')}")
        print(f"Nome: {turma_teste.get('nome')}")
        print(f"Ciclo: {turma_teste.get('ciclo')}")
        print(f"Unidade: {turma_teste.get('unidade_id')}")
        print(f"Curso: {turma_teste.get('curso_id')}")
        
        print("\nCAMPOS DE INSTRUTOR:")
        # Verificar todos os campos de instrutor
        if 'instrutor_id' in turma_teste:
            print(f"  ❌ instrutor_id (antigo): {turma_teste['instrutor_id']}")
        
        if 'instrutor_ids' in turma_teste:
            ids = turma_teste['instrutor_ids']
            print(f"  ✅ instrutor_ids (novo): {ids}")
            print(f"  📊 Quantidade: {len(ids)}")
            
            if len(ids) == 2:
                print("\n🎉 SUCESSO! TURMA TEM 2 INSTRUTORES!")
                
                # Buscar nomes
                resp_users = requests.get(f"{BACKEND_URL}/users", headers=headers)
                usuarios = resp_users.json()
                
                for i, uid in enumerate(ids, 1):
                    usuario = next((u for u in usuarios if u['id'] == uid), None)
                    if usuario:
                        print(f"  {i}. {usuario['nome']} ({usuario['email']})")
            else:
                print(f"\n⚠️ ATENÇÃO: Turma tem {len(ids)} instrutor(es)")
        else:
            print("  ❌ instrutor_ids NÃO existe!")
        
        print("\n" + "=" * 80)
    else:
        print("\n❌ Turma 'Teste' NÃO encontrada no Render")
        print(f"Total de turmas retornadas: {len(turmas)}")

if __name__ == "__main__":
    buscar_turma_teste()
