import requests
from bs4 import BeautifulSoup

def buscar_jurisprudencia_tjsp(
    termo=None, numero_processo=None, relator=None, orgao_julgador=None,
    classe=None, comarca=None, assunto=None, data_inicio=None, data_fim=None, pagina=1
):
    url = "https://esaj.tjsp.jus.br/cjsg/resultadoCompleta.do"
    params = {
        "cdForo": "0",
        "pagina": pagina,
        "pesquisaLivre": termo or "",
        "numeroProcesso": numero_processo or "",
        "classe": classe or "",
        "relator": relator or "",
        "orgaoJulgador": orgao_julgador or "",
        "assunto": assunto or "",
        "comarca": comarca or "",
        "dataJulgamentoInicio": data_inicio or "",
        "dataJulgamentoFim": data_fim or ""
    }
    resposta = requests.get(url, params=params, headers={"User-Agent": "ConsultaAutomatizadaAdvogado/1.0"})
    if resposta.status_code != 200:
        return {"erro": "Falha ao acessar TJSP"}
    soup = BeautifulSoup(resposta.text, "html.parser")
    resultados = []
    for item in soup.select(".resultado"):
        ementa = item.select_one(".ementa")
        numero = item.select_one(".processo")
        data_julgamento = item.select_one(".data-julgamento")
        resultados.append({
            "Número do processo": numero.get_text(strip=True) if numero else "",
            "Data do julgamento": data_julgamento.get_text(strip=True) if data_julgamento else "",
            "Ementa": ementa.get_text(strip=True) if ementa else "",
        })
    return {
        "tribunal": "TJSP",
        "resultados": resultados if resultados else ["Nenhuma decisão localizada com esses filtros."]
    }
