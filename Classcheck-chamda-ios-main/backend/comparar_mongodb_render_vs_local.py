#!/usr/bin/env python3
"""
Verificar qual MongoDB o Render está usando
"""

import requests
import re

BACKEND_URL = "https://sistema-ios-backend.onrender.com/api"

# Login admin
resp = requests.post(f"{BACKEND_URL}/auth/login", 
                    json={"email": "jesiel.junior@ios.org.br", "senha": "b99018cd"})
token = resp.json()['access_token']
headers = {"Authorization": f"Bearer {token}"}

print("=" * 80)
print("VERIFICANDO CONEXÃO MONGODB DO RENDER")
print("=" * 80)

# Buscar todas as turmas
resp = requests.get(f"{BACKEND_URL}/classes", headers=headers)
turmas = resp.json()

print(f"\nTotal de turmas retornadas pelo Render: {len(turmas)}")
print("\nÚltimas 5 turmas:")
for t in turmas[-5:]:
    print(f"  - {t['nome']} (ID: {t['id'][:20]}...)")

print("\n" + "=" * 80)
print("COMPARANDO COM MONGODB ATLAS (local)")
print("=" * 80)

from pymongo import MongoClient

MONGO_URI_LOCAL = "mongodb+srv://educacional_db_user:qpvR7mlOHSoxwvQ8@chamada-prod.nr10evs.mongodb.net/?retryWrites=true&w=majority&appName=chamada-prod"

try:
    client = MongoClient(MONGO_URI_LOCAL, serverSelectionTimeoutMS=10000)
    db = client["IOS-SISTEMA-CHAMADA"]
    
    turmas_local = list(db.turmas.find({"ativo": True}))
    print(f"\nTotal de turmas no MongoDB Atlas local: {len(turmas_local)}")
    print("\nÚltimas 5 turmas (local):")
    for t in turmas_local[-5:]:
        print(f"  - {t.get('nome')} (ID: {t.get('id', '')[:20]}...)")
    
    # Verificar se a turma Teste existe localmente
    turma_teste_local = db.turmas.find_one({"nome": "Teste"})
    if turma_teste_local:
        print(f"\n✅ Turma 'Teste' encontrada LOCALMENTE:")
        print(f"   ID: {turma_teste_local['id']}")
        print(f"   instrutor_ids: {turma_teste_local.get('instrutor_ids')}")
    else:
        print("\n❌ Turma 'Teste' NÃO encontrada localmente")
    
    client.close()
    
    print("\n" + "=" * 80)
    print("CONCLUSÃO:")
    print("=" * 80)
    if len(turmas) == len(turmas_local):
        print("✅ Render e local CONECTADOS NO MESMO MONGODB")
        print(f"   Ambos têm {len(turmas)} turmas")
    else:
        print("❌ DATABASES DIFERENTES!")
        print(f"   Render: {len(turmas)} turmas")
        print(f"   Local: {len(turmas_local)} turmas")
        print("\n⚠️ Render pode estar usando variável de ambiente diferente!")
        
except Exception as e:
    print(f"\n❌ Erro ao conectar MongoDB local: {e}")
    print("   Mas Render funcionou, então Render usa outro MongoDB!")
