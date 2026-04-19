# Local RAG Assistant

Sistema local de assistência de conhecimento baseado em RAG (Retrieval-Augmented Generation).

## Estrutura do Projeto

- **backend/**: API FastAPI, processamento de documentos e busca vetorial.
- **frontend/**: Interface Vue.js 3 com Tailwind CSS.
- **e2e-tests/**: Testes de ponta a ponta com Playwright.
- **docker-compose.yml**: Orquestração de serviços.
- **Makefile**: Comandos de automação para facilitar o desenvolvimento.

## Requisitos

- Docker e Docker Compose
- Make
- Python 3.12+ (opcional para rodar localmente)
- Node.js 20+ e pnpm (opcional para rodar localmente)

## Setup Rápido

1. **Configurar variáveis de ambiente:**
   Copie o arquivo `.env.example` para `.env` na raiz:
   ```bash
   cp .env.example .env
   ```
   Edite o `.env` e adicione sua `OPENROUTER_API_KEY`.

2. **Subir a aplicação:**
   ```bash
   make up
   ```

3. **Executar migrations:**
   ```bash
   make migrate
   ```

A aplicação estará disponível em:
- **Frontend**: http://localhost:5173
- **Backend (API Docs)**: http://localhost:8000/docs

## Comandos do Makefile

O `Makefile` centraliza os comandos mais comuns:

| Comando | Descrição |
|---------|-----------|
| `make up` | Inicia todos os containers em background. |
| `make down` | Para todos os containers. |
| `make logs` | Visualiza os logs em tempo real. |
| `make migrate` | Aplica migrations do Alembic no banco de dados. |
| `make test` | Executa a suíte de testes E2E. |
| `make shell-backend` | Acessa o terminal do container backend. |
| `make shell-db` | Acessa o CLI do PostgreSQL. |
| `make clean` | Remove containers, volumes e limpa dados de upload. |

## Testes

Para rodar os testes de ponta a ponta:
```bash
make test
```

## Desenvolvimento Local (Sem Docker)

Se preferir rodar os componentes separadamente fora do Docker, você pode usar:
```bash
make install
```
Isso instalará as dependências do backend e frontend em suas respectivas pastas. Veja os READMEs internos em `backend/` e `frontend/` para mais detalhes.
