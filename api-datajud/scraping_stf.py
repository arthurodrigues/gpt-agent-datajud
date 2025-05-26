def consultar_processo_stf(numero_processo):
    url = f"https://portal.stf.jus.br/processos/detalhe.asp?incidente={numero_processo}"
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers)
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
