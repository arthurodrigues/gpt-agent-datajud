from fastapi import FastAPI, Request
from scraping_stj import buscar_jurisprudencia_stj
from scraping_tjsp import buscar_jurisprudencia_tjsp
from scraping_stf import buscar_jurisprudencia_stf
from scraping_tjsp import consultar_processo_tjsp
from scraping_stj import consultar_processo_stj
from scraping_stf import consultar_processo_stf

app = FastAPI(
    title="API Unificada de Consulta Processual e Jurisprudência",
    description="Consulta processual e jurisprudência em STJ, TJSP e STF.",
    version="1.0.0"
)

@app.post("/processos")
async def pesquisar_processos(request: Request):
    body = await request.json()
    numero_processo = body.get("numero_processo")
    tribunal = (body.get("tribunal") or "").upper()

    if not numero_processo:
        return {"erro": "É obrigatório informar o número do processo."}

    if tribunal == "TJSP":
        resultado = consultar_processo_tjsp(numero_processo)
    elif tribunal == "STJ":
        resultado = consultar_processo_stj(numero_processo)
    elif tribunal == "STF":
        resultado = consultar_processo_stf(numero_processo)
    else:
        return {"erro": "Tribunal não suportado ou não informado (use TJSP, STJ ou STF)."}

    return resultado

@app.post("/jurisprudencia")
async def pesquisar_jurisprudencia(request: Request):
    body = await request.json()
    palavra_chave = body.get("palavra_chave")
    tribunal = (body.get("tribunal") or "").upper()
    pagina = body.get("pagina", 1)
    tamanho = body.get("tamanho", 5)

    if not palavra_chave:
        return {"erro": "É obrigatório informar uma palavra-chave para busca de jurisprudência."}

    if tribunal == "TJSP":
        resultados = buscar_jurisprudencia_tjsp(
            termo_livre=palavra_chave,
            pagina=pagina,
            tamanho=tamanho
        )
    elif tribunal == "STJ":
        resultados = buscar_jurisprudencia_stj(
            termo_livre=palavra_chave,
            pagina=pagina,
            tamanho=tamanho
        )
    elif tribunal == "STF":
        resultados = buscar_jurisprudencia_stf(
            termo_livre=palavra_chave,
            pagina=pagina,
            tamanho=tamanho
        )
    else:
        return {"erro": "Tribunal não suportado ou não informado (use TJSP, STJ ou STF)."}

    return {"total": len(resultados), "jurisprudencias": resultados}
