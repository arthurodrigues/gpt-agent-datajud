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
