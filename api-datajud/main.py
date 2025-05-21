from fastapi import FastAPI
from pydantic import BaseModel
from datajud_stj import pesquisar_stj_datajud

app = FastAPI()

class ConsultaRequest(BaseModel):
    numero_processo: str = None
    nome_parte: str = None
    tribunal: str = None
    assunto: str = None
    pagina: int = 1
    tamanho: int = 5

@app.post("/pesquisar")
def pesquisar(req: ConsultaRequest):
    resultados = pesquisar_stj_datajud(
        numero_processo=req.numero_processo,
        nome_parte=req.nome_parte,
        tribunal=req.tribunal,
        assunto=req.assunto,
        pagina=req.pagina,
        tamanho=req.tamanho
    )
    return resultados
