def consultar_processo_stj(numero_processo):
    url = f"https://processo.stj.jus.br/processo/pesquisa/?aplicacao=processos&numero_processo={numero_processo}"
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, "html.parser")
    # Os campos e classes podem variar, adapte conforme necessário!
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
