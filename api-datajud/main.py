from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Any
from fastapi.responses import JSONResponse

app = FastAPI(
    title="API Unificada de Consulta Processual e Jurisprudência",
    description="Consulta processos e jurisprudência com múltiplos filtros (STJ, STF, TJSP).",
    version="1.0.0",
    contact={
        "name": "Seu Nome/Time",
        "url": "https://www.seusite.com"
    }
)

# ==== MODELOS DE REQUISIÇÃO E RESPOSTA ====

class Movimentacao(BaseModel):
    descricao: str

class Processo(BaseModel):
    numero_processo: str
    nome_parte: Optional[str]
    tribunal: Optional[str]
    classe: Optional[str]
    assunto: Optional[str]
    orgao_julgador: Optional[str]
    data_distribuicao: Optional[str]
    movimentacoes: Optional[List[str]] = []

class Jurisprudencia(BaseModel):
    tribunal: str
    numero_processo: str
    classe: Optional[str]
    orgao_julgador: Optional[str]
    relator: Optional[str]
    data_julgamento: Optional[str]
    ementa: Optional[str]
    inteiro_teor_url: Optional[str]

class FiltrosProcesso(BaseModel):
    numero_processo: Optional[str] = None
    nome_parte: Optional[str] = None
    tribunal: Optional[str] = None
    classe: Optional[str] = None
    assunto: Optional[str] = None
    orgao_julgador: Optional[str] = None
    data_inicio: Optional[str] = None
    data_fim: Optional[str] = None
    pagina: int = 1
    tamanho: int = 5

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

# ==== ENDPOINTS ====

@app.post("/processos")
def pesquisar_processos(filtros: FiltrosProcesso):
    """
    Pesquisa processos judiciais (STJ, STF, TJSP, etc) por filtros avançados.
    """
    # Exemplo: aqui você faria requests para a API do DataJud ou scraping conforme filtros
    # Exemplo "mock":
    resultados = [
        Processo(
            numero_processo="1234567-89.2022.8.26.0100",
            nome_parte="João da Silva",
            tribunal="TJSP",
            classe="Ação de Indenização",
            assunto="Danos Morais",
            orgao_julgador="5ª Câmara de Direito Privado",
            data_distribuicao="2022-01-10",
            movimentacoes=["Distribuição em 10/01/2022", "Sentença em 05/05/2022"]
        )
    ]
    return {"total": len(resultados), "processos": [p.dict() for p in resultados]}

@app.post("/jurisprudencia")
def pesquisar_jurisprudencia(filtros: FiltrosJurisprudencia):
    """
    Pesquisa jurisprudência (STJ, STF, TJSP, etc) por filtros avançados.
    """
    # Exemplo: aqui você integraria a busca DataJud, scraping ou qualquer fonte
    resultados = [
        Jurisprudencia(
            tribunal="STJ",
            numero_processo="REsp 123456/SP",
            classe="Recurso Especial",
            orgao_julgador="Terceira Turma",
            relator="Ministro João Mendes",
            data_julgamento="2023-06-20",
            ementa="A recusa injustificada de seguradora em pagar indenização caracteriza dano moral.",
            inteiro_teor_url="https://www.stj.jus.br/inteiroteor/123456"
        )
    ]
    return {"total": len(resultados), "jurisprudencias": [j.dict() for j in resultados]}

# Você pode personalizar a saída para deixá-la mais amigável (Markdown, HTML ou estruturada para consumo do agente GPT).

# Para rodar localmente:
# uvicorn main:app --reload

