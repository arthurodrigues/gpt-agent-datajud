
# API Unificada de Consulta Processual e Jurisprudência

Esta API tem por objetivo fornecer uma **consulta centralizada e automatizada** de processos judiciais e jurisprudência dos principais tribunais brasileiros: **STJ, TJSP e STF**.

## Funcionalidades

- **Consulta processual unificada:**  
  Consulta processos judiciais por número do processo nos três tribunais, além de permitir buscas por nome de parte e assunto no STJ (via DataJud).

- **Pesquisa de jurisprudência:**  
  Pesquisa decisões e acórdãos por palavra-chave nos três tribunais.

## Endpoints

### `POST /processos`

Consulta processual por número de processo.  
- **STJ:** Permite busca por número (scraping) ou por parte/assunto (DataJud).
- **TJSP e STF:** Apenas busca por número do processo.

#### Parâmetros de entrada (JSON)

```json
{
  "numero_processo": "string",
  "nome_parte": "string",          // Apenas STJ (via DataJud)
  "assunto": "string",             // Apenas STJ (via DataJud)
  "tribunal": "STJ|TJSP|STF",
  "pagina": 1,                     // Opcional (DataJud)
  "tamanho": 5                     // Opcional (DataJud)
}
```

#### Resposta esperada

- Dados do processo encontrado, ou mensagem de erro informando limitação de busca por parte/assunto.

---

### `POST /jurisprudencia`

Pesquisa jurisprudências por palavra-chave.

#### Parâmetros de entrada (JSON)

```json
{
  "palavra_chave": "string",
  "tribunal": "STJ|TJSP|STF",
  "pagina": 1,         // Opcional
  "tamanho": 5         // Opcional
}
```

#### Resposta esperada

- Lista de decisões/acórdãos, contendo número do processo, ementa e link do inteiro teor (quando disponível).

---

## Restrições e Avisos Importantes

- **Busca processual por nome de parte ou assunto só é suportada no STJ (via DataJud).**  
  TJSP e STF não oferecem essa funcionalidade por meios públicos ou automáticos.

- **Pesquisa de jurisprudência por nome de parte não é suportada em nenhum tribunal via API/scraping.**  
  Utilize sempre palavra-chave, número de processo, relator, classe ou órgão julgador.

- **Links de inteiro teor dependem da disponibilidade pública dos tribunais.**
- **A API ainda está em desenvolvimento e pode sofrer ajustes.**

---

## Instalação

```bash
git clone <este-repo>
cd <este-repo>
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

---

## Licença

Projeto para fins acadêmicos e experimentais.  
Consulte a legislação vigente antes de uso profissional ou comercial.

---

## Responsável

Desenvolvido por Arthur Rodrigues.  
Em caso de dúvidas, sugestões ou contribuições, entre em contato.

