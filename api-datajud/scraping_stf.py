import requests
from bs4 import BeautifulSoup

def buscar_jurisprudencia_stf(
    termo=None, numero_processo=None, relator=None,
    orgao_julgador=None, tipo_decisao=None, data_inicio=None, data_fim=None, pagina=1
):
    # Atenção: O STF utiliza POST, com nomes dos campos sensíveis a alterações
    url = "https://redir.stf.jus.br/pesquisas/pages/jurisprudencia/resultadoPesquisaJurisprudencia.jsf"
    data = {
        "formularioPesquisa:j_id452": termo or "",
        "formularioPesquisa:numeroProcesso": numero_processo or "",
        "formularioPesquisa:relator": relator or "",
        "formularioPesquisa:orgaoJulgador": orgao_julgador or "",
        "formularioPesquisa:tipoDecisao": tipo_decisao or "",
        "formularioPesquisa:dataJulgamentoInicio": data_inicio or "",
        "formularioPesquisa:dataJulgamentoFim": data_fim or "",
        "formularioPesquisa:pagina": str(pagina),
        "javax.faces.ViewState": "stateless"
    }
    resposta = requests.post(url, data=data, headers={"User-Agent": "ConsultaAutomatizadaAdvogado/1.0"})
    if resposta.status_code != 200:
        return {"erro": "Falha ao acessar STF"}
    soup = BeautifulSoup(resposta.text, "html.parser")
    resultados = []
    for item in soup.select(".detalheJurisprudencia"):
        ementa = item.select_one(".ementaJurisprudencia")
        numero = item.select_one(".numeroProcessoJurisprudencia")
        data_julgamento = item.select_one(".dataJulgamentoJurisprudencia")
        # Link do inteiro teor
        link = item.select_one("a[href*='paginadorpub/paginador.jsp?docTP=AC&docID=']")
        inteiro_teor_url = "https://redir.stf.jus.br" + link['href'] if link else ""
        resultados.append({
            "numero_processo": numero.get_text(strip=True) if numero else "",
            "data_julgamento": data_julgamento.get_text(strip=True) if data_julgamento else "",
            "ementa": ementa.get_text(strip=True) if ementa else "",
            "inteiro_teor_url": inteiro_teor_url
        })
    return {
        "tribunal": "STF",
        "resultados": resultados if resultados else ["Nenhuma decisão localizada com esses filtros."]
    }
