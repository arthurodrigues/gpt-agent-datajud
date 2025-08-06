# Consulta Jurídica Unificada

Este projeto fornece uma API unificada para consultas processuais e de
jurisprudência nos principais tribunais brasileiros (STJ, STF e TJSP). Ele
foi desenhado para ser utilizado como **ação personalizada** no ChatGPT,
permitindo que assistentes jurídicos obtenham informações confiáveis sem
alucinações.

## Componentes

- **`openai.yaml`**: arquivo de configuração da ação para o ChatGPT. Ele
  descreve o nome, a funcionalidade e o esquema de autenticação, apontando
  para o `openapi.json` gerado pela aplicação.
- **`app/main.py`**: aplicação FastAPI expondo rotas para consultar
  processos (`/processo`) e pesquisar jurisprudência (`/jurisprudencia`).
- **`app/tribunal.py`**: implementa as funções de acesso aos tribunais,
  utilizando a API oficial DataJud (quando disponível) ou raspagem de
  páginas públicas com `requests` e `BeautifulSoup`.
- **`requirements.txt`**: dependências Python necessárias.

## Como executar localmente

1. Clone este repositório e navegue até a pasta `consulta_juridica_agent`.
2. (Opcional) Crie um ambiente virtual e ative-o.
3. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

4. (Opcional) Crie um arquivo `.env` ou exporte a variável `DATAJUD_API_KEY`
   com a sua chave de API do DataJud (CNJ) para melhorar a consulta no STJ:

   ```bash
   export DATAJUD_API_KEY=...   # sua chave do DataJud
   ```

5. Inicie a aplicação com `uvicorn`:

   ```bash
   uvicorn consulta_juridica_agent.app.main:app --reload
   ```

6. Acesse `http://localhost:8000/docs` para visualizar a documentação
   interativa e testar as rotas.

## Uso como ação do ChatGPT

Para registrar esta API como uma ação personalizada do ChatGPT, hospede a
aplicação em um endpoint acessível publicamente e referencie a URL do
``openapi.json`` no arquivo `openai.yaml`. Em seguida, importe a ação no
ChatGPT (menu de extensões → Ações personalizadas) e forneça o arquivo
`openai.yaml`.

Uma vez instalada, a ação pode ser invocada automaticamente pelo ChatGPT
quando um usuário solicitar consultas de processos ou jurisprudência.