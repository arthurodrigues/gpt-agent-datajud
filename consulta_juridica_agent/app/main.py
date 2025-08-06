"""
Aplicação FastAPI para consultas processuais e de jurisprudência.

Este módulo define uma API HTTP com duas rotas principais:

* ``POST /processo``: recebe um número de processo e a sigla do tribunal e
  retorna dados estruturados sobre o processo.
* ``POST /jurisprudencia``: recebe uma palavra‑chave, a sigla do tribunal e
  parâmetros opcionais de paginação e retorna resultados de jurisprudência.

Esta API pode ser registrada como uma ação personalizada no ChatGPT por meio
do arquivo ``openai.yaml``, permitindo que a IA recupere dados reais dos
tribunais sem alucinar informações.
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from .tribunal import search_process, search_jurisprudence

app = FastAPI(
    title="Consulta Jurídica Unificada",
    description="API para consulta de processos e pesquisa de jurisprudência nos tribunais STJ, STF e TJSP.",
    version="0.1.0",
)


class ProcessoRequest(BaseModel):
    """Modelo de entrada para consulta processual."""

    numero_processo: str = Field(..., description="Número do processo a consultar.")
    tribunal: str = Field(..., description="Sigla do tribunal (STJ, STF ou TJSP).")


class JurisprudenciaRequest(BaseModel):
    """Modelo de entrada para pesquisa de jurisprudência."""

    palavra_chave: str = Field(..., description="Termo de busca nas jurisprudências.")
    tribunal: str = Field(..., description="Sigla do tribunal (STJ, STF ou TJSP).")
    pagina: Optional[int] = Field(1, description="Número da página de resultados.")
    tamanho: Optional[int] = Field(5, description="Quantidade de resultados a retornar.")


@app.post("/processo")
async def consultar_processo(req: ProcessoRequest):
    """
    Consulta dados de um processo em um tribunal específico.

    Retorna um dicionário com número do processo, partes, classe, assunto e
    movimentações. Caso o tribunal não seja suportado ou o processo não seja
    encontrado, lança HTTP 404.
    """
    result = search_process(req.tribunal, req.numero_processo)
    if result is None:
        raise HTTPException(status_code=404, detail="Processo não encontrado ou tribunal não suportado.")
    return result


@app.post("/jurisprudencia")
async def consultar_jurisprudencia(req: JurisprudenciaRequest):
    """
    Pesquisa jurisprudência em um tribunal específico.

    Retorna um objeto com a contagem total de resultados retornados e a lista
    correspondente com dados de jurisprudência. Caso o tribunal não seja
    suportado, uma lista vazia é retornada.
    """
    resultados = search_jurisprudence(req.tribunal, req.palavra_chave, req.pagina or 1, req.tamanho or 5)
    return {"total": len(resultados), "resultados": resultados}
