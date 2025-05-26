import requests
from bs4 import BeautifulSoup

def consultar_processo_tjsp(numero_processo):
    url = "https://esaj.tjsp.jus.br/cpopg/open.do"
    params = {"gateway": "true", "numeroProcesso": numero_processo}
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, params=params, headers=headers)
    if not resp.ok:
        return None
    soup = BeautifulSoup(resp.text, "html.parser")
    partes = []
    for parte in soup.select("div .nomeParteEAdvogado"):
        partes.append(parte.get_text(strip=True))
    classe = soup.find("span", id="classeProcesso").get_text(strip=True) if soup.find("span", id="classeProcesso") else ""
    assunto = soup.find("span", id="assuntoProcesso").get_text(strip=True) if soup.find("span", id="assuntoProcesso") else ""
    movimentacoes = []
    for mov in soup.select("tr .descricaoMovimentacao"):
        movimentacoes.append(mov.get_text(strip=True))
    return {
        "numero_processo": numero_processo,
        "partes": partes,
        "classe": classe,
        "assunto": assunto,
        "movimentacoes": movimentacoes
    }

def buscar_jurisprudencia_tjsp(termo_livre, pagina=1, tamanho=5):
    url = "https://esaj.tjsp.jus.br/cjsg/resultadoCompleta.do"
    params = {
        "cdForo": "",
        "cdTipoDocumento": "",
        "dtRelatorio": "",
        "dePesquisa": termo_livre or "",
        "pagina": pagina
    }
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.post(url, data=params, headers=headers)
    if not resp.ok:
        return []
    soup = BeautifulSoup(resp.text, "html.parser")
    resultados = []
    blocos = soup.select(".fundocinza1, .fundocinza2")
    for bloco in blocos:
        numero_proc = bloco.select_one(".numeroProcesso").get_text(strip=True) if bloco.select_one(".numeroProcesso") else ""
        ementa = bloco.select_one(".ementa").get_text(strip=True) if bloco.select_one(".ementa") else ""
        link_tag = bloco.find("a", string="Inteiro Teor")
        inteiro_teor_url = (
            "https://esaj.tjsp.jus.br" + link_tag["href"] if link_tag and link_tag.get("href") else "Não disponível"
        )
        resultados.append({
            "numero_processo": numero_proc,
            "ementa": ementa,
            "jurisprudencia_url": inteiro_teor_url
        })
        if len(resultados) >= tamanho:
            break
    return resultados
