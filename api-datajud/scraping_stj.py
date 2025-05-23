import requests
from bs4 import BeautifulSoup

def buscar_jurisprudencia_stj(
    termo=None, numero_processo=None, classe=None, orgao_julgador=None,
    relator=None, data_inicio=None, data_fim=None, pagina=1
):
    url = "https://jurisprudencia.stj.jus.br/externo_controlador_consulta_externa.do"
    params = {
        "acao": "pesquisar",
        "tipo_visualizacao": "RESUMIDA",
        "pagina": pagina
    }
    if termo:
        params["termo"] = termo
    if numero_processo:
        params["numeroProcesso"] = numero_processo
    if classe:
        params["classe"] = classe
    if orgao_julgador:
        params["orgaoJulgador"] = orgao_julgador
    if relator:
        params["relator"] = relator
    if data_inicio:
        params["dataInicioJulgamento"] = data_inicio  # formato DD/MM/AAAA
    if data_fim:
        params["dataFimJulgamento"] = data_fim

    resposta = requests.get(url, params=params, headers={"User-Agent": "ConsultaAutomatizadaAdvogado/1.0"})
    if resposta.status_code != 200:
        return {"erro": "Falha ao acessar STJ"}
    soup = BeautifulSoup(resposta.text, "html.parser")
    resultados = []
    for item in soup.select(".resultado-jurisprudencia"):
        ementa = item.select_one(".ementa")
        numero = item.select_one(".numero-proc")
        data = item.select_one(".data-julgamento")
        link = item.select_one("a[title='Inteiro Teor']")
        inteiro_teor_url = "https://jurisprudencia.stj.jus.br" + link["href"] if link else None
        resultados.append({
            "numero_processo": numero.get_text(strip=True) if numero else "",
            "data_julgamento": data.get_text(strip=True) if data else "",
            "ementa": ementa.get_text(strip=True) if ementa else "",
            "inteiro_teor_url": inteiro_teor_url if inteiro_teor_url else "",
        })
    return {
        "tribunal": "STJ",
        "resultados": resultados if resultados else ["Nenhuma decisão localizada com esses filtros."]
    }
