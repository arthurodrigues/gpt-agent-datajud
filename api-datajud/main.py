from fastapi import FastAPI
from pydantic import BaseModel
from datajud_stj import pesquisar_stj_datajud
from scraping_stj import buscar_jurisprudencia_stj
from scraping_stf import buscar_jurisprudencia_stf
from scraping_tjsp import buscar_jurisprudencia_tjsp

app = FastAPI()

class ConsultaProcessosRequest(BaseModel):
    numero_processo: str = None
    nome_parte: str = None
    tribunal: str = None
    assunto: str = None
    pagina: int = 1
    tamanho: int = 5

class ConsultaJurisRequest(BaseModel):
    tribunal: str
    termo: str = None
    numero_processo: str = None
    classe: str = None
    orgao_julgador: str = None
    relator: str = None
    data_inicio: str = None
    data_fim: str = None
    comarca: str = None
    assunto: str = None
    tipo_decisao: str = None
    pagina: int = 1

@app.post("/processos")
def processos(req: ConsultaProcessosRequest):
    resultados = pesquisar_stj_datajud(
        numero_processo=req.numero_processo,
        nome_parte=req.nome_parte,
        tribunal=req.tribunal,
        assunto=req.assunto,
        pagina=req.pagina,
        tamanho=req.tamanho
    )
    return resultados

@app.post("/jurisprudencia")
def jurisprudencia(req: ConsultaJurisRequest):
    t = req.tribunal.lower()
    if t == "stj":
        return buscar_jurisprudencia_stj(
            termo=req.termo,
            numero_processo=req.numero_processo,
            classe=req.classe,
            orgao_julgador=req.orgao_julgador,
            relator=req.relator,
            data_inicio=req.data_inicio,
            data_fim=req.data_fim,
            pagina=req.pagina
        )
    elif t == "stf":
        return buscar_jurisprudencia_stf(
            termo=req.termo,
            numero_processo=req.numero_processo,
            relator=req.relator,
            orgao_julgador=req.orgao_julgador,
            tipo_decisao=req.tipo_decisao,
            data_inicio=req.data_inicio,
            data_fim=req.data_fim,
            pagina=req.pagina
        )
    elif t == "tjsp":
        return buscar_jurisprudencia_tjsp(
            termo=req.termo,
            numero_processo=req.numero_processo,
            relator=req.relator,
            orgao_julgador=req.orgao_julgador,
            classe=req.classe,
            comarca=req.comarca,
            assunto=req.assunto,
            data_inicio=req.data_inicio,
            data_fim=req.data_fim,
            pagina=req.pagina
        )
    else:
        return {"erro": "Tribunal não suportado. Use 'stj', 'stf' ou 'tjsp'."}
