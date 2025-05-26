import requests
from bs4 import BeautifulSoup

def consultar_processo_stf(numero_processo):
    url = f"https://portal.stf.jus.br/processos/detalhe.asp?incidente={numero_processo}"
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers)
    if not resp.ok:
        return None
    soup = BeautifulSoup(resp.text, "html.parser")
    partes = []
    for parte in soup.select(".nomeParte"):
        partes.append(parte.get_text(strip=True))
    classe = soup.find("td", class_="classeProcesso").get_text(strip=True) if soup.find("td", class_="classeProcesso") else ""
    assunto = soup.find("td", class_="assuntoProcesso").get_text(strip=True) if soup.find("td", class_="assuntoProcesso") else ""
    movimentacoes = []
    for mov in soup.select(".movimentacao"):
        movimentacoes.append(mov.get_text(strip=True))
    return {
        "numero_processo": numero_processo,
        "partes": partes,
        "classe": classe,
        "assunto": assunto,
        "movimentacoes": movimentacoes
    }

def buscar_jurisprudencia_stf(termo_livre, pagina=1, tamanho=5):
    url = "https://jurisprudencia.stf.jus.br/pages/search/decision/decision.xhtml"
    params = {
        "termo": termo_livre or "",
        "currentPage": str(pagina),
        "pageSize": str(tamanho)
    }
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(
        "https://jurisprudencia.stf.jus.br/pages/search/decision/decision.xhtml?termo=" + (termo_livre or ""),
        headers=headers
    )
    if not resp.ok:
        return []
    soup = BeautifulSoup(resp.text, "html.parser")
    resultados = []
    blocos = soup.select("div.result")
    for bloco in blocos:
        numero_proc = bloco.find("span", class_="processo")
        numero_proc = numero_proc.get_text(strip=True) if numero_proc else ""
        ementa = bloco.find("div", class_="ementa")
        ementa = ementa.get_text(strip=True) if ementa else ""
        link_tag = bloco.find("a", string="Inteiro Teor")
        jurisprudencia_url = link_tag['href'] if link_tag and link_tag.get("href") else "Não disponível"
        resultados.append({
            "numero_processo": numero_proc,
            "ementa": ementa,
            "jurisprudencia_url": jurisprudencia_url
        })
        if len(resultados) >= tamanho:
            break
    return resultados
