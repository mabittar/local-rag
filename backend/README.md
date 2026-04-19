# Local RAG Platform - Backend API

Backend API RESTful para POC de plataforma RAG (Retrieval-Augmented Generation) usando FastAPI, PostgreSQL com pgvector, e OpenRouter API.

## Stack Tecnológico

- **Framework**: FastAPI (Python 3.12+)
- **Banco de Dados**: PostgreSQL 18+ com extensão pgvector
- **ORM**: SQLModel + SQLAlchemy 2.0
- **Autenticação**: JWT (JSON Web Tokens)
- **LLM Provider**: OpenRouter API (modelos free)
- **Vector Store**: PostgreSQL + pgvector
- **Migrations**: Alembic

## Requisitos

### Dependências de Sistema

- Python 3.12+
- PostgreSQL 18+ (com pgvector instalado)
- Docker e Docker Compose (opcional, para PostgreSQL)

## Setup Inicial

### 1. Iniciar PostgreSQL com Docker (Recomendado)

```bash
# No diretório raiz do projeto (um nível acima de backend/)
cd /home/mmb/pprojects/local-rag
docker-compose up -d postgres
```

Aguarde 10-20 segundos para o PostgreSQL inicializar completamente.

### 2. Criar Extensão pgvector

```bash
# Conectar ao banco e criar extensão
docker exec -it localrag-postgres psql -U localrag -d localrag -c "CREATE EXTENSION IF NOT EXISTS vector;"
docker exec -it localrag-postgres psql -U localrag -d localrag -c "CREATE EXTENSION IF NOT EXISTS pgcrypto;"
```

### 3. Configurar Ambiente Python

```bash
cd backend

# Criar ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt
```

### 4. Configurar Variáveis de Ambiente

```bash
# Copiar template
cp .env.example .env

# Editar .env com suas configurações
# Principalmente: OPENROUTER_API_KEY e DATABASE_URL
```

Exemplo de `.env`:

```env
# API
APP_NAME=LocalRAG
DEBUG=true
API_HOST=0.0.0.0
API_PORT=8000

# Database
DATABASE_URL=postgresql+asyncpg://localrag:localrag123@localhost:5433/localrag
PGVECTOR_DIMS=384

# Security
SECRET_KEY=change-this-secret-key-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=60

# OpenRouter (obrigatório)
OPENROUTER_API_KEY=sk-or-v1-seu-token-aqui
OPENROUTER_MODEL=meta-llama/llama-3.2-3b-instruct:free
OPENROUTER_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# RAG Settings
CHUNK_SIZE=512
CHUNK_OVERLAP=50
TOP_K=5
TEMPERATURE=0.7
MAX_TOKENS=2048

# Storage
UPLOAD_DIR=./data/uploads
MAX_FILE_SIZE=104857600
ALLOWED_EXTENSIONS=pdf,txt,docx,md
```

### 5. Criar Diretório de Uploads

```bash
mkdir -p data/uploads
```

## Migrations e Seed

### Executar Migrations (Alembic)

```bash
# Aplicar todas as migrations pendentes
alembic upgrade head
```

Para criar uma nova migration após alterar os modelos:

```bash
# Gerar nova migration automaticamente
alembic revision --autogenerate -m "descrição da alteração"

# Aplicar
alembic upgrade head
```

### Seed de Dados (Automático)

O seed do usuário padrão é executado automaticamente quando a aplicação inicia.

**Credenciais padrão:**
- Username: `localuser`
- Password: `localuser123`

Para forçar a recriação do usuário seed:

```python
# Script para resetar senha do usuário localuser
python -c "
import asyncio
from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.models.user import User
from sqlalchemy import select

async def reset_password():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.username == 'localuser'))
        user = result.scalar_one_or_none()
        
        if user:
            user.hashed_password = get_password_hash('localuser123')
            await session.commit()
            print('Password reset successfully')
        else:
            print('User not found')

asyncio.run(reset_password())
"
```

## Executando o Backend

### Desenvolvimento

```bash
# Certifique-se de estar no diretório backend com o venv ativado
cd backend
source .venv/bin/activate

# Iniciar servidor com reload automático
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

O servidor estará disponível em: http://localhost:8000

### Produção

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Verificar Instalação

### 1. Health Check

```bash
curl http://localhost:8000/health
```

Resposta esperada:
```json
{"status": "healthy", "version": "1.0.0"}
```

### 2. Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "localuser", "password": "localuser123"}'
```

Resposta esperada:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

## Documentação da API

Após iniciar o servidor:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## Estrutura do Projeto

```
backend/
├── alembic/                   # Migrations
│   ├── versions/              # Arquivos de migration
│   ├── env.py                 # Configuração Alembic
│   └── script.py.mako         # Template de migration
├── app/
│   ├── api/v1/                # Routers da API
│   │   ├── auth.py            # Endpoints de autenticação
│   │   ├── documents.py       # Endpoints de documentos
│   │   └── chat.py            # Endpoints de chat
│   ├── core/                  # Configurações core
│   │   ├── config.py          # Settings Pydantic
│   │   ├── database.py        # Conexão DB + seed
│   │   └── security.py        # JWT, bcrypt
│   ├── infrastructure/        # Integrações externas
│   │   ├── openrouter.py      # Cliente OpenRouter
│   │   ├── document_processor.py  # Extração de texto
│   │   └── pgvector_store.py  # Busca vetorial
│   ├── models/                # SQLModel models
│   │   ├── user.py
│   │   ├── document.py
│   │   └── chat.py
│   ├── schemas/               # Pydantic schemas
│   │   ├── auth.py
│   │   ├── document.py
│   │   └── chat.py
│   └── services/              # Lógica de negócio
│       ├── auth_service.py
│       ├── document_service.py
│       ├── chat_service.py
│       └── rag_service.py
├── main.py                    # Entry point FastAPI
├── alembic.ini               # Configuração Alembic
├── requirements.txt
└── .env
```

## Endpoints Principais

### Autenticação

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/auth/login` | Login (localuser/localuser123) |

### Documentos

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/documents/upload` | Upload de arquivo (multipart) |
| GET | `/api/documents` | Listar documentos (paginado) |
| GET | `/api/documents/{id}` | Detalhes do documento |
| DELETE | `/api/documents/{id}` | Excluir documento e chunks |

### Chat

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/chat/sessions` | Criar sessão de chat |
| GET | `/api/chat/sessions` | Listar sessões |
| DELETE | `/api/chat/sessions/{id}` | Excluir sessão |
| GET | `/api/chat/sessions/{id}/messages` | Histórico de mensagens |
| POST | `/api/chat/stream` | Streaming SSE com RAG |

## Exemplos de Uso

### Login e Obter Token

```bash
# Login
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "localuser", "password": "localuser123"}' \
  | jq -r '.access_token')

echo "Token: $TOKEN"
```

### Upload de Documento

```bash
curl -X POST http://localhost:8000/api/documents/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/caminho/para/documento.pdf"
```

### Criar Sessão de Chat

```bash
curl -X POST http://localhost:8000/api/chat/sessions \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Minha Conversa"}'
```

### Chat com Streaming (SSE)

```bash
curl -X POST http://localhost:8000/api/chat/stream \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"session_id": 1, "message": "O que diz o documento?"}' \
  -N
```

## Configuração OpenRouter

1. Crie uma conta em https://openrouter.ai
2. Gere uma API Key em Settings > API Keys
3. Configure no `.env`: `OPENROUTER_API_KEY=sk-or-v1-...`

Modelos free disponíveis:
- `meta-llama/llama-3.2-3b-instruct:free` (padrão)
- `mistralai/mistral-7b-instruct:free`
- `deepseek/deepseek-chat:free`

## Comandos Úteis

### Database

```bash
# Aplicar migrations
alembic upgrade head

# Reverter última migration
alembic downgrade -1

# Ver histórico
alembic history

# Criar nova migration
alembic revision --autogenerate -m "add new field"

# Reset completo (cuidado!)
alembic downgrade base
alembic upgrade head
```

### Docker

```bash
# Iniciar PostgreSQL
docker-compose up -d postgres

# Ver logs
docker-compose logs -f postgres

# Parar
docker-compose down

# Limpar volumes (remove todos os dados!)
docker-compose down -v

# Conectar ao banco via CLI
docker exec -it localrag-postgres psql -U localrag -d localrag
```

## Troubleshooting

### Erro: `relation "users" does not exist`

O banco não foi inicializado. Execute migrations:

```bash
alembic upgrade head
```

Ou reinicie a aplicação (init_db roda automaticamente).

### Erro: `pgvector extension not found`

Crie a extensão manualmente:

```bash
docker exec -it localrag-postgres psql -U localrag -d localrag -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### Erro: `Invalid salt` ao fazer login

O hash da senha está em formato inválido. Resetar:

```python
# Executar no diretório backend
python -c "
import asyncio
from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.models.user import User
from sqlalchemy import select

async def fix():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.username == 'localuser'))
        user = result.scalar_one_or_none()
        if user:
            user.hashed_password = get_password_hash('localuser123')
            await session.commit()
            print('Password reset')

asyncio.run(fix())
"
```

### Erro: `OpenRouter API key not configured`

Configure a variável de ambiente:

```bash
export OPENROUTER_API_KEY=sk-or-v1-...
```

### Erro: `Connection refused` ao conectar no PostgreSQL

Verifique se o container está rodando:

```bash
docker-compose ps
docker-compose logs postgres
```

### Limpar tudo e recomeçar

```bash
# Parar containers
docker-compose down -v

# Remover arquivos de upload
rm -rf data/uploads/*

# Recriar banco
docker-compose up -d postgres
sleep 10

# Criar extensões
docker exec -it localrag-postgres psql -U localrag -d localrag -c "CREATE EXTENSION IF NOT EXISTS vector;"
docker exec -it localrag-postgres psql -U localrag -d localrag -c "CREATE EXTENSION IF NOT EXISTS pgcrypto;"

# Aplicar migrations
cd backend
alembic upgrade head

# Iniciar app
uvicorn main:app --reload
```

## Desenvolvimento

### Executando Testes

```bash
pytest tests/
```

### Lint e Formatação

```bash
# Formatar código
black app/

# Ordenar imports
isort app/

# Verificar lint
ruff check app/
```

## Recursos

- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLModel](https://sqlmodel.tiangolo.com/)
- [Alembic](https://alembic.sqlalchemy.org/)
- [OpenRouter](https://openrouter.ai/docs)
- [pgvector](https://github.com/pgvector/pgvector)

## Licença

Projeto POC - Uso interno apenas.
