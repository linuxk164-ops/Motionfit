#!/usr/bin/env python
"""Teste básico da API Artemis com Gemini"""
from Artemis import app
import json

app.config['TESTING'] = True
client = app.test_client()

print("=" * 60)
print("TESTES DA API ARTEMIS - GOOGLE GEMINI")
print("=" * 60)

# Teste 1: Requisição válida
print("\n[TESTE 1] Requisição válida com pergunta")
response = client.post('/perguntas', 
    data=json.dumps({'pergunta': 'Qual é a capital do Brasil?'}),
    content_type='application/json'
)
print(f"Status HTTP: {response.status_code}")
data = response.get_json()
print(f"Chaves na resposta: {list(data.keys())}")
if response.status_code == 200:
    print(f"✓ Pergunta processada com sucesso")
    resposta = data.get('resposta', '')
    print(f"Primeiros 100 caracteres da resposta: {resposta[:100]}")
else:
    print(f"✗ Erro: {data}")

# Teste 2: Sem a chave 'pergunta'
print("\n[TESTE 2] Requisição sem a chave 'pergunta'")
response = client.post('/perguntas',
    data=json.dumps({}),
    content_type='application/json'
)
print(f"Status HTTP: {response.status_code}")
print(f"Resposta: {response.get_json()}")
if response.status_code == 400:
    print("✓ Validação funcionando corretamente")

# Teste 3: Pergunta vazia
print("\n[TESTE 3] Pergunta vazia/whitespace")
response = client.post('/perguntas',
    data=json.dumps({'pergunta': '   '}),
    content_type='application/json'
)
print(f"Status HTTP: {response.status_code}")
print(f"Resposta: {response.get_json()}")
if response.status_code == 400:
    print("✓ Validação de pergunta vazia funcionando")

# Teste 4: Tipo errado para pergunta
print("\n[TESTE 4] Pergunta com tipo errado (número)")
response = client.post('/perguntas',
    data=json.dumps({'pergunta': 123}),
    content_type='application/json'
)
print(f"Status HTTP: {response.status_code}")
print(f"Resposta: {response.get_json()}")
if response.status_code == 400:
    print("✓ Validação de tipo funcionando")

print("\n" + "=" * 60)
print("TESTES COMPLETADOS")
print("=" * 60)
