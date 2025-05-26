import requests
from bs4 import BeautifulSoup

def consultar_processo_stj(numero_processo):
    # Exemplo básico, adapte conforme layout real do site
    url = f"https://processo.stj.jus.br/processo/pesquisa/?aplicacao=processos&numero_processo={numero_processo}"
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers)
    if not resp.ok:
        return None
    soup = BeautifulSoup(resp.text, "html.parser")
    partes = []
    for parte in soup.select(".partes"):
        partes.append(parte.get_text(strip=True))
    classe = soup.find("span", class_="classe").get_text(strip=True) if soup.find("span", class_="classe") else ""
    assunto = soup.find("span", class_="assunto").get_text(strip=True) if soup.find("span", class_="assunto") else ""
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

def buscar_jurisprudencia_stj(palavra_chave, pagina=1, tamanho=5):
    url = "https://scon.stj.jus.br/SCON/pesquisar.jsp"
    params = {
        "livre": palavra_chave or "",
        "b": "ACOR",
        "p": "true",
        "thesaurus": "JURIDICO",
        "l": tamanho,
        "i": pagina,
        "tp": "T"
    }
    resposta = requests.get(url, params=params)
    if not resposta.ok:
        return []
    soup = BeautifulSoup(resposta.text, "html.parser")
    resultados = []
    for item in soup.select('.resumo_jurisprudencia'):
        numero_proc = item.select_one('.processo').get_text(strip=True) if item.select_one('.processo') else ""
        ementa = item.select_one('.ementa').get_text(strip=True) if item.select_one('.ementa') else ""
        link_tag = item.find('a', string="Inteiro Teor")
        inteiro_teor_link = "https://scon.stj.jus.br" + link_tag.get("href") if link_tag else "Não disponível"
        resultados.append({
            "numero_processo": numero_proc,
            "ementa": ementa,
            "jurisprudencia_url": inteiro_teor_link
        })
        if len(resultados) >= tamanho:
            break
    return resultados
