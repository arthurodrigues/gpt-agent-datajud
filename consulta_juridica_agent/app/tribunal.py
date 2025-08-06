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


def _verificar_url(url: str) -> bool:
    """Verifica se a URL retorna um código de status HTTP 200.

    Esta função envia uma requisição HEAD (follow redirects) para garantir que
    o link apontado existe e está acessível. Em caso de exceção ou código
    diferente de 200, considera-se que o link é inválido.

    :param url: URL a verificar.
    :returns: True se o endereço for acessível, False caso contrário.
    """
    try:
        resp = requests.head(url, allow_redirects=True, timeout=10)
        return resp.status_code == 200
    except Exception:
        return False

# API DataJud – utiliza uma chave de API configurada em variável de ambiente.
#
# A documentação oficial do DataJud explica que a autenticação é feita
# através de uma chave pública (“API Key”) disponibilizada pelo CNJ. Essa chave
# é exibida na página de acesso da API e pode ser alterada a qualquer momento【366122704607526†L34-L48】.
# Para incorporar a chave nas requisições é necessário adicionar um cabeçalho
# ``Authorization`` com o valor ``ApiKey <chave>`` – note a grafia utilizada
# nos exemplos oficiais【513198736461717†L83-L87】. Para manter o agente funcional
# mesmo quando nenhuma variável de ambiente está configurada, definimos abaixo
# a chave vigente publicada na documentação pública. Caso o CNJ publique uma
# nova chave, basta definir a variável de ambiente ``DATAJUD_API_KEY`` com
# essa nova string.
DEFAULT_DATAJUD_API_KEY: str = (
    "cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw=="
)
DATAJUD_API_KEY: str = os.getenv("DATAJUD_API_KEY", DEFAULT_DATAJUD_API_KEY)
DATAJUD_STJ_URL: str = "https://api-publica.datajud.cnj.jus.br/api_publica_stj/_search"
DATAJUD_TJSP_URL: str = "https://api-publica.datajud.cnj.jus.br/api_publica_tjsp/_search"


def _consultar_processo_stj(numero_processo: str) -> Optional[Dict[str, Any]]:
    """Consulta um processo no STJ usando a API DataJud ou por scraping.

    :param numero_processo: número do processo a ser consultado.
    :returns: dicionário com dados do processo ou ``None`` se ocorrer erro.
    """
    # Se houver chave (pode ser a fornecida na documentação ou definida pelo usuário),
    # tente utilizar a API DataJud. De acordo com o exemplo oficial【344784192551802†L2-L4】,
    # a pesquisa por número de processo utiliza o operador ``match`` sem precisar
    # encapsular em ``bool``. Limitamos a ``size`` em 1 para obter apenas o
    # primeiro documento que corresponda ao número informado.
    if DATAJUD_API_KEY:
        # Remover formatação (pontos, hífens) do número de processo para
        # atender à exigência da API DataJud de usar a numeração sem formatação【264484894236365†L41-L42】.
        numero_limpo = "".join(ch for ch in numero_processo if ch.isdigit())
        # Consulta via API DataJud usando uma busca simples por ``numeroProcesso``. A
        # especificação indica o uso do cabeçalho "ApiKey"【513198736461717†L83-L87】 e
        # recomenda limitar o tamanho (size) quando se deseja apenas um documento.
        payload = {
            "query": {"match": {"numeroProcesso": numero_limpo or numero_processo}},
            "size": 1,
        }
        headers = {
            "Authorization": f"ApiKey {DATAJUD_API_KEY}",
            "Content-Type": "application/json",
        }
        try:
            resp = requests.post(DATAJUD_STJ_URL, json=payload, headers=headers, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            hits = data.get("hits", {}).get("hits", [])
            if hits:
                # Extraia o primeiro documento retornado. Os campos disponíveis variam
                # conforme o tribunal, mas os metadados básicos são comuns.
                doc = hits[0].get("_source", {})
                numero = doc.get("numeroProcesso")
                classe_dict = doc.get("classe") or doc.get("classeProcessual") or {}
                classe = classe_dict.get("nome") if isinstance(classe_dict, dict) else classe_dict
                assuntos = doc.get("assuntos") or []
                assunto = ", ".join([a.get("nome") for a in assuntos if isinstance(a, dict)]) or None
                movimentos = doc.get("movimentos") or doc.get("andamentos") or []
                movimentacoes = [m.get("nome") or m.get("movimento") for m in movimentos if isinstance(m, dict)]
                # O DataJud não fornece as partes do processo nos exemplos públicos, portanto
                # retornamos lista vazia para manter compatibilidade da estrutura.
                return {
                    "numero_processo": numero,
                    "partes": [],
                    "classe": classe,
                    "assunto": assunto,
                    "movimentacoes": movimentacoes,
                }
        except requests.RequestException:
            # Se a chamada à API falhar (por exemplo, indisponibilidade do DataJud),
            # prosseguir com o scraping do site do STJ.
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
    # Primeiro tente a API DataJud para o TJSP. Assim como no STJ, a pesquisa
    # utiliza o campo ``numeroProcesso`` e retorna metadados básicos. Se a API
    # falhar ou não retornar resultados, recorre-se ao scraping do ESAJ.
    if DATAJUD_API_KEY:
        # Remover formatação do número de processo antes de consultar a API
        numero_limpo = "".join(ch for ch in numero_processo if ch.isdigit())
        payload = {
            "query": {"match": {"numeroProcesso": numero_limpo or numero_processo}},
            "size": 1,
        }
        headers = {
            "Authorization": f"ApiKey {DATAJUD_API_KEY}",
            "Content-Type": "application/json",
        }
        try:
            resp = requests.post(DATAJUD_TJSP_URL, json=payload, headers=headers, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            hits = data.get("hits", {}).get("hits", [])
            if hits:
                doc = hits[0].get("_source", {})
                numero = doc.get("numeroProcesso")
                classe_dict = doc.get("classe") or {}
                classe = classe_dict.get("nome") if isinstance(classe_dict, dict) else classe_dict
                assuntos = doc.get("assuntos") or []
                assunto = ", ".join([a.get("nome") for a in assuntos if isinstance(a, dict)]) or None
                movimentos = doc.get("movimentos") or []
                movimentacoes = [m.get("nome") for m in movimentos if isinstance(m, dict)]
                return {
                    "numero_processo": numero,
                    "partes": [],
                    "classe": classe,
                    "assunto": assunto,
                    "movimentacoes": movimentacoes,
                }
        except requests.RequestException:
            # Se a API estiver indisponível, cairá para o scraping abaixo
            pass
    # Fallback via scraping no site ESAJ (consulta processual padrão do TJSP).
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
            # Link do inteiro teor pode vir como caminho relativo. Verificar diferentes domínios.
            link_tag = item.find("a", string="Inteiro Teor")
            inteiro_teor_link: str
            if link_tag and link_tag.get("href"):
                href = link_tag.get("href")
                # Se o href já contiver http, use diretamente
                if href.startswith("http"):
                    candidato = href
                else:
                    # Primeira tentativa: prefixo scon.stj.jus.br
                    candidato = f"https://scon.stj.jus.br{href}"
                # Verificar se o link retornado pelo site é acessível.
                # Não tente adivinhar domínios alternativos; se o candidato não existir, não retorne link.
                inteiro_teor_link = candidato if _verificar_url(candidato) else "Não disponível"
            else:
                inteiro_teor_link = "Não disponível"
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
            jurisprudencia_url: str
            if link_tag and link_tag.get("href"):
                href = link_tag.get("href")
                # Se for relativo, prefixar com domínio do STF
                if href.startswith("http"):
                    candidato = href
                else:
                    candidato = f"https://jurisprudencia.stf.jus.br{href}"
                # Verificar se o link responde
                jurisprudencia_url = candidato if _verificar_url(candidato) else "Não disponível"
            else:
                jurisprudencia_url = "Não disponível"
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
            inteiro_teor_url: str
            if link_tag and link_tag.get("href"):
                href = link_tag.get("href")
                if href.startswith("http"):
                    candidato = href
                else:
                    candidato = f"https://esaj.tjsp.jus.br{href}"
                inteiro_teor_url = candidato if _verificar_url(candidato) else "Não disponível"
            else:
                inteiro_teor_url = "Não disponível"
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