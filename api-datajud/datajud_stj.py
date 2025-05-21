import requests

API_KEY = "cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw=="
URL = "https://api-publica.datajud.cnj.jus.br/api_publica_stj/_search"

def pesquisar_stj_datajud(numero_processo=None, nome_parte=None, tribunal=None, assunto=None, pagina=1, tamanho=5):
    must_clauses = []

    if numero_processo:
        must_clauses.append({"match": {"numeroProcesso": numero_processo}})
    if nome_parte:
        must_clauses.append({"match": {"partes.nome": nome_parte}})
    if tribunal:
        must_clauses.append({"match": {"tribunal": tribunal}})
    if assunto:
        must_clauses.append({"match": {"assuntos.nome": assunto}})

    if must_clauses:
        query = {"bool": {"must": must_clauses}}
    else:
        query = {"match_all": {}}

    payload = {
        "from": (pagina - 1) * tamanho,
        "size": tamanho,
        "query": query
    }

    headers = {
        "Authorization": f"APIKey {API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(URL, json=payload, headers=headers, timeout=30)
    if response.status_code == 200:
        return response.json()
    else:
        print("Erro:", response.status_code)
        print(response.text)
        return None
