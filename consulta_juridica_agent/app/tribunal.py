"""
Módulo de consultas a tribunais brasileiros.

Este módulo fornece funções para consultar processos e jurisprudência nos
tribunais STJ, STF e TJSP. As implementações reutilizam raspadores simples
baseados em ``requests`` e ``BeautifulSoup`` e, quando possível, a API
oficial DataJud do Conselho Nacional de Justiça (CNJ). Cada função tenta
conservar a estrutura dos dados retornados sem realizar inferências ou
preenchimentos artificiais. Em caso de falha na requisição ou ausência de
suporte, as funções retornam ``None`` ou listas vazias.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import requests
from bs4 import BeautifulSoup

# API DataJud – utiliza uma chave de API configurada em variável de ambiente.
DATAJUD_API_KEY: Optional[str] = os.getenv("DATAJUD_API_KEY")
DATAJUD_STJ_URL: str = "https://api-publica.datajud.cnj.jus.br/api_publica_stj/_search"


def _consultar_processo_stj(numero_processo: str) -> Optional[Dict[str, Any]]:
    """Consulta um processo no STJ usando a API DataJud ou por scraping.

    :param numero_processo: número do processo a ser consultado.
    :returns: dicionário com dados do processo ou ``None`` se ocorrer erro.
    """
    # Se houver chave, tente utilizar a API DataJud.
    if DATAJUD_API_KEY:
        must_clause = {"match": {"numeroProcesso": numero_processo}}
        payload = {"from": 0, "size": 1, "query": {"bool": {"must": [must_clause]}}}
        headers = {
            "Authorization": f"APIKey {DATAJUD_API_KEY}",
            "Content-Type": "application/json",
        }
        try:
            resp = requests.post(DATAJUD_STJ_URL, json=payload, headers=headers, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            hits = data.get("hits", {}).get("hits", [])
            if not hits:
                return None
            doc = hits[0].get("_source", {})
            return {
                "numero_processo": doc.get("numeroProcesso"),
                "partes": [p.get("nome") for p in doc.get("partes", [])],
                "classe": doc.get("classeProcessual"),
                "assunto": ", ".join([a.get("nome") for a in doc.get("assuntos", [])]) or None,
                "movimentacoes": [m.get("movimento") for m in doc.get("andamentos", [])],
            }
        except requests.RequestException:
            # Se falhar, caia para o scraping.
            pass
    # Fallback para scraping básico do site do STJ.
    url = f"https://processo.stj.jus.br/processo/pesquisa/?aplicacao=processos&numero_processo={numero_processo}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=30)
        if not r.ok:
            return None
        soup = BeautifulSoup(r.text, "html.parser")
        partes = [p.get_text(strip=True) for p in soup.select(".partes")]  # tipo: ignore[index]
        classe_tag = soup.find("span", class_="classe")
        classe = classe_tag.get_text(strip=True) if classe_tag else None
        assunto_tag = soup.find("span", class_="assunto")
        assunto = assunto_tag.get_text(strip=True) if assunto_tag else None
        movimentacoes = [m.get_text(strip=True) for m in soup.select(".movimentacao")]  # tipo: ignore[index]
        return {
            "numero_processo": numero_processo,
            "partes": partes,
            "classe": classe,
            "assunto": assunto,
            "movimentacoes": movimentacoes,
        }
    except Exception:
        return None


def _consultar_processo_stf(numero_processo: str) -> Optional[Dict[str, Any]]:
    """Consulta um processo no STF por scraping.

    :param numero_processo: incidente/ID do processo no STF.
    :returns: dicionário com dados do processo ou ``None`` se ocorrer erro.
    """
    url = f"https://portal.stf.jus.br/processos/detalhe.asp?incidente={numero_processo}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        if not resp.ok:
            return None
        soup = BeautifulSoup(resp.text, "html.parser")
        partes = [p.get_text(strip=True) for p in soup.select(".nomeParte")]  # tipo: ignore[index]
        classe_tag = soup.find("td", class_="classeProcesso")
        classe = classe_tag.get_text(strip=True) if classe_tag else None
        assunto_tag = soup.find("td", class_="assuntoProcesso")
        assunto = assunto_tag.get_text(strip=True) if assunto_tag else None
        movimentacoes = [m.get_text(strip=True) for m in soup.select(".movimentacao")]  # tipo: ignore[index]
        return {
            "numero_processo": numero_processo,
            "partes": partes,
            "classe": classe,
            "assunto": assunto,
            "movimentacoes": movimentacoes,
        }
    except Exception:
        return None


def _consultar_processo_tjsp(numero_processo: str) -> Optional[Dict[str, Any]]:
    """Consulta um processo no TJSP por scraping.

    :param numero_processo: número do processo (formato CNJ) a consultar.
    :returns: dicionário com dados do processo ou ``None``.
    """
    url = "https://esaj.tjsp.jus.br/cpopg/open.do"
    params = {"gateway": "true", "numeroProcesso": numero_processo}
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, params=params, headers=headers, timeout=30)
        if not r.ok:
            return None
        soup = BeautifulSoup(r.text, "html.parser")
        partes = [p.get_text(strip=True) for p in soup.select("div .nomeParteEAdvogado")]
        classe_tag = soup.find("span", id="classeProcesso")
        classe = classe_tag.get_text(strip=True) if classe_tag else None
        assunto_tag = soup.find("span", id="assuntoProcesso")
        assunto = assunto_tag.get_text(strip=True) if assunto_tag else None
        movimentacoes = [m.get_text(strip=True) for m in soup.select("tr .descricaoMovimentacao")]
        return {
            "numero_processo": numero_processo,
            "partes": partes,
            "classe": classe,
            "assunto": assunto,
            "movimentacoes": movimentacoes,
        }
    except Exception:
        return None


def _buscar_jurisprudencia_stj(palavra_chave: str, pagina: int = 1, tamanho: int = 5) -> List[Dict[str, Any]]:
    """Pesquisa jurisprudência no STJ.

    :param palavra_chave: termo livre da pesquisa.
    :param pagina: número da página (base 1).
    :param tamanho: quantidade de resultados a retornar.
    :returns: lista de dicionários com número do processo, ementa e URL do inteiro teor.
    """
    url = "https://scon.stj.jus.br/SCON/pesquisar.jsp"
    params = {
        "livre": palavra_chave or "",
        "b": "ACOR",
        "p": "true",
        "thesaurus": "JURIDICO",
        "l": tamanho,
        "i": pagina,
        "tp": "T",
    }
    try:
        resp = requests.get(url, params=params, timeout=30)
        if not resp.ok:
            return []
        soup = BeautifulSoup(resp.text, "html.parser")
        resultados: List[Dict[str, Any]] = []
        for item in soup.select(".resumo_jurisprudencia"):
            numero_proc_tag = item.select_one(".processo")
            numero_proc = numero_proc_tag.get_text(strip=True) if numero_proc_tag else ""
            ementa_tag = item.select_one(".ementa")
            ementa = ementa_tag.get_text(strip=True) if ementa_tag else ""
            link_tag = item.find("a", string="Inteiro Teor")
            inteiro_teor_link = (
                "https://scon.stj.jus.br" + link_tag.get("href")
                if link_tag and link_tag.get("href")
                else "Não disponível"
            )
            resultados.append(
                {
                    "numero_processo": numero_proc,
                    "ementa": ementa,
                    "jurisprudencia_url": inteiro_teor_link,
                }
            )
            if len(resultados) >= tamanho:
                break
        return resultados
    except Exception:
        return []


def _buscar_jurisprudencia_stf(palavra_chave: str, pagina: int = 1, tamanho: int = 5) -> List[Dict[str, Any]]:
    """Pesquisa jurisprudência no STF.

    :param palavra_chave: termo de busca.
    :param pagina: número da página (base 1).
    :param tamanho: quantidade de resultados a retornar.
    :returns: lista de resultados com número do processo, ementa e URL do inteiro teor.
    """
    # A página do STF constrói os resultados via JS; aqui utilizamos scraping simples.
    base_url = "https://jurisprudencia.stf.jus.br/pages/search/decision/decision.xhtml"
    try:
        # Construção da URL com query string direta, pois a navegação utiliza parâmetros dinâmicos.
        resp = requests.get(f"{base_url}?termo={palavra_chave or ''}", timeout=30)
        if not resp.ok:
            return []
        soup = BeautifulSoup(resp.text, "html.parser")
        resultados: List[Dict[str, Any]] = []
        for bloco in soup.select("div.result"):
            numero_proc_tag = bloco.find("span", class_="processo")
            numero_proc = numero_proc_tag.get_text(strip=True) if numero_proc_tag else ""
            ementa_tag = bloco.find("div", class_="ementa")
            ementa = ementa_tag.get_text(strip=True) if ementa_tag else ""
            link_tag = bloco.find("a", string="Inteiro Teor")
            jurisprudencia_url = link_tag['href'] if link_tag and link_tag.get("href") else "Não disponível"
            resultados.append(
                {
                    "numero_processo": numero_proc,
                    "ementa": ementa,
                    "jurisprudencia_url": jurisprudencia_url,
                }
            )
            if len(resultados) >= tamanho:
                break
        return resultados
    except Exception:
        return []


def _buscar_jurisprudencia_tjsp(palavra_chave: str, pagina: int = 1, tamanho: int = 5) -> List[Dict[str, Any]]:
    """Pesquisa jurisprudência no TJSP.

    :param palavra_chave: termo de busca.
    :param pagina: número da página (base 1).
    :param tamanho: quantidade de resultados a retornar.
    :returns: lista de resultados.
    """
    url = "https://esaj.tjsp.jus.br/cjsg/resultadoCompleta.do"
    data = {
        "cdForo": "",
        "cdTipoDocumento": "",
        "dtRelatorio": "",
        "dePesquisa": palavra_chave or "",
        "pagina": pagina,
    }
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.post(url, data=data, headers=headers, timeout=30)
        if not r.ok:
            return []
        soup = BeautifulSoup(r.text, "html.parser")
        resultados: List[Dict[str, Any]] = []
        for bloco in soup.select(".fundocinza1, .fundocinza2"):
            numero_proc_tag = bloco.select_one(".numeroProcesso")
            numero_proc = numero_proc_tag.get_text(strip=True) if numero_proc_tag else ""
            ementa_tag = bloco.select_one(".ementa")
            ementa = ementa_tag.get_text(strip=True) if ementa_tag else ""
            link_tag = bloco.find("a", string="Inteiro Teor")
            inteiro_teor_url = (
                "https://esaj.tjsp.jus.br" + link_tag["href"]
                if link_tag and link_tag.get("href")
                else "Não disponível"
            )
            resultados.append(
                {
                    "numero_processo": numero_proc,
                    "ementa": ementa,
                    "jurisprudencia_url": inteiro_teor_url,
                }
            )
            if len(resultados) >= tamanho:
                break
        return resultados
    except Exception:
        return []


def search_process(tribunal: str, numero_processo: str) -> Optional[Dict[str, Any]]:
    """Despacha a consulta do processo para o tribunal apropriado.

    :param tribunal: sigla do tribunal (STJ, STF, TJSP).
    :param numero_processo: número/identificador do processo.
    :returns: dados do processo ou ``None`` se não suportado ou erro.
    """
    tribunal = (tribunal or "").upper()
    if not numero_processo:
        return None
    if tribunal == "STJ":
        return _consultar_processo_stj(numero_processo)
    if tribunal == "STF":
        return _consultar_processo_stf(numero_processo)
    if tribunal == "TJSP":
        return _consultar_processo_tjsp(numero_processo)
    return None


def search_jurisprudence(
    tribunal: str,
    palavra_chave: str,
    pagina: int = 1,
    tamanho: int = 5,
) -> List[Dict[str, Any]]:
    """Despacha a pesquisa de jurisprudência para o tribunal apropriado.

    :param tribunal: sigla do tribunal (STJ, STF, TJSP).
    :param palavra_chave: termo de busca.
    :param pagina: página de resultados (base 1).
    :param tamanho: quantidade de resultados por página.
    :returns: lista de resultados.
    """
    tribunal = (tribunal or "").upper()
    if not palavra_chave:
        return []
    if tribunal == "STJ":
        return _buscar_jurisprudencia_stj(palavra_chave, pagina, tamanho)
    if tribunal == "STF":
        return _buscar_jurisprudencia_stf(palavra_chave, pagina, tamanho)
    if tribunal == "TJSP":
        return _buscar_jurisprudencia_tjsp(palavra_chave, pagina, tamanho)
    return []