from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional

from scraping_stj import buscar_jurisprudencia_stj
from scraping_stf import buscar_jurisprudencia_stf
from scraping_tjsp import buscar_jurisprudencia_tjsp

app = FastAPI(
    title="API Unificada de Consulta Processual e Jurisprudência",
    description="Consulta processos e jurisprudência com múltiplos filtros (STJ, STF, TJSP).",
    version="1.0.0"
)

class Jurisprudencia(BaseModel):
    tribunal: str
    numero_processo: Optional[str]
    classe: Optional[str]
    orgao_julgador: Optional[str]
    relator: Optional[str]
    data_julgamento: Optional[str]
    ementa: Optional[str]
    inteiro_teor_url: Optional[str]

class FiltrosJurisprudencia(BaseModel):
    tribunal: Optional[str] = None
    palavra_chave: Optional[str] = None
    numero_processo: Optional[str] = None
    orgao_julgador: Optional[str] = None
    classe: Optional[str] = None
    data_inicio: Optional[str] = None
    data_fim: Optional[str] = None
    pagina: int = 1
    tamanho: int = 5

@app.post("/jurisprudencia")
def pesquisar_jurisprudencia(filtros: FiltrosJurisprudencia):
    resultados = []

    # Chama os módulos conforme o filtro de tribunal
    if not filtros.tribunal or filtros.tribunal.upper() == "STJ":
        stj_result = buscar_jurisprudencia_stj(
            termo=filtros.palavra_chave,
            numero_processo=filtros.numero_processo,
            classe=filtros.classe,
            orgao_julgador=filtros.orgao_julgador,
            data_inicio=filtros.data_inicio,
            data_fim=filtros.data_fim,
            pagina=filtros.pagina
        )
        for item in stj_result["resultados"]:
            item["tribunal"] = "STJ"
            resultados.append(item)

    if not filtros.tribunal or filtros.tribunal.upper() == "STF":
        stf_result = buscar_jurisprudencia_stf(
            termo=filtros.palavra_chave,
            numero_processo=filtros.numero_processo,
            orgao_julgador=filtros.orgao_julgador,
            data_inicio=filtros.data_inicio,
            data_fim=filtros.data_fim,
            pagina=filtros.pagina
        )
        for item in stf_result["resultados"]:
            item["tribunal"] = "STF"
            resultados.append(item)

    if not filtros.tribunal or filtros.tribunal.upper() == "TJSP":
        tjsp_result = buscar_jurisprudencia_tjsp(
            termo=filtros.palavra_chave,
            numero_processo=filtros.numero_processo,
            orgao_julgador=filtros.orgao_julgador,
            data_inicio=filtros.data_inicio,
            data_fim=filtros.data_fim,
            pagina=filtros.pagina
        )
        for item in tjsp_result["resultados"]:
            item["tribunal"] = "TJSP"
            resultados.append(item)

    return {"total": len(resultados), "jurisprudencias": resultados}
