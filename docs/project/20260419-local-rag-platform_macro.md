# Plataforma RAG Local - Macro Definições

**Date**: 19/04/2026
**Last Update**: 19/04/2026
**Version**: 1.2
**Priority**: 🔴 HIGH

**Changelog v1.2**:
- POC simplificada: 1 usuário local (multi-user via Google SSO/Auth0 é funcionalidade futura)
- Backend atualizado: Python 3.12.8, FastAPI latest
- Frontend alterado: Vue.js 3 (Composition API) com dark mode exclusivo
- Suporte dual para LLM: OpenRouter API (modelos free) + Ollama local opcional
- Removida restrição de hardware AMD - POC funciona em qualquer hardware
- Removido SvelteKit (replaced by Vue.js)

---

## 1. Visão Geral do Projeto

### 1.1 Propósito
Desenvolver uma plataforma de Retrieval-Augmented Generation (RAG) operando exclusivamente em ambiente local, permitindo que dois usuários interajam com documentos privados através de linguagem natural, com garantia total de privacidade dos dados e aproveitamento otimizado de hardware AMD.

### 1.2 Escopo (POC)
**Incluído**:
- Ingestão, processamento, indexação e consulta de documentos
- Interface web para gerenciamento e chat
- Suporte a múltiplos formatos de arquivo (PDF, TXT, DOCX, MD)
- Citação de fontes nas respostas
- 1 usuário local simples (para POC)
- Suporte dual LLM: OpenRouter API (modelos free) + Ollama local (opcional)

**Excluído**:
- Treinamento de modelos de linguagem do zero
- Suporte a múltiplos idiomas além do português e inglês
- Sincronização com serviços em nuvem
- Autenticação multiusuário (será implementado via Google SSO/Auth0 em versão futura)
- Restrição de hardware específico (AMD GPU)
- Não é necessário hardware local GPU para POC inicial

---

## 2. Business Objective
Criar uma plataforma RAG para consulta inteligente de documentos em linguagem natural, com interface Vue.js dark mode, usando OpenRouter API para modelos free em POC, e com arquitetura preparada para evolução com autenticação Google SSO/Auth0.

---

## 3. Hardware de Referência

### 3.1 POC (Qualquer Hardware)
| Componente | Especificação |
|------------|---------------|
| CPU | Qualquer processador moderno |
| RAM | 8GB+ (recomendado 16GB) |
| SO | Linux/macOS/Windows |
| GPU | Não necessário para POC |

### 3.2 Produção com Ollama Local (Opcional)
| Componente | Especificação |
|------------|---------------|
| GPU | AMD RX 9070 XT (16GB VRAM) - [OPCIONAL] |
| RAM | 32GB |
| SO | CachyOS (Linux) |
| Backend ROCm | 6.2+ |

---

## 4. Technical Stack

### 4.1 Linguagens e Frameworks Principais

| Camada | Tecnologia | Versão | Propósito |
|--------|------------|--------|-----------|
| Backend API | Python | 3.12.8 | Lógica de negócio e API REST |
| Framework API | FastAPI | latest | Endpoints RESTful com async/await |
| RAG Framework | LlamaIndex | 0.14.x | Orquestração de RAG e ingestão |
| Frontend | Vue.js | 3.x | Interface web reativa (Composition API) |
| Frontend UI | TailwindCSS | 3.x+ | Estilização dark mode exclusivo |
| State Management | Pinia | 2.x | Gerenciamento de estado Vue |
| Router | Vue Router | 4.x | Roteamento SPA |
| ORM | SQLModel | 0.0.x | Modelagem de dados SQL |

### 4.2 Infraestrutura de IA

| Componente | Tecnologia | Versão | Propósito |
|------------|------------|--------|-----------|
| LLM API | OpenRouter | API v1 | API unificada para modelos free |
| LLM Local | Ollama | 0.5.x | Inferência local (opcional/futuro) |
| Vector Database | PostgreSQL + pgvector | 18+ / 0.8.x | Armazenamento de embeddings e metadados |
| Extension | pgvector | 0.8.x+ | Extensão PostgreSQL para vetores |
| GPU Compute | AMD ROCm | 6.2+ | Aceleração GPU (opcional/futuro) |

### 4.3 Modelos Recomendados (POC - OpenRouter Free)

| Tipo | Modelo | Provedor | Uso | Notas |
|------|--------|----------|-----|-------|
| LLM Principal | meta-llama/llama-3.2-3b-instruct:free | Meta | Chat e respostas | Modelo free via OpenRouter |
| LLM Alternativo | mistralai/mistral-7b-instruct:free | Mistral AI | Respostas mais elaboradas | Modelo free via OpenRouter |
| LLM Avançado | deepseek/deepseek-chat:free | DeepSeek | Raciocínio complexo | Modelo free via OpenRouter |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 | HuggingFace | Geração de embeddings | Via OpenRouter embeddings API |

### 4.4 Modelos Opcionais (Ollama Local - Futuro)

| Tipo | Modelo | Parâmetros | VRAM Estimada | Uso |
|------|--------|------------|---------------|-----|
| LLM Local | llama3.2 | 3B | ~2.5GB | Chat offline (requer GPU) |
| Embeddings Local | nomic-embed-text | ~137M | ~400MB | Embeddings offline |

### 4.5 Bibliotecas Python Principais

```
# Core
llama-index-core>=0.14.0
llama-index-vector-stores-postgres>=0.3.0

# LLM Providers - Dual Support
openrouter>=0.3.0              # OpenRouter API SDK
openai>=1.0.0                # Para integração OpenRouter (OpenAI compatible)
llama-index-embeddings-openai>=0.3.0  # Embeddings via OpenRouter

# Ollama (opcional para modo local)
llama-index-embeddings-ollama>=0.5.0
llama-index-llms-ollama>=0.5.0

# API
fastapi>=0.115.0
uvicorn[standard]>=0.34.0
pydantic>=2.0.0
sqlmodel>=0.0.14

# PostgreSQL + pgvector
psycopg[binary]>=3.2.0
pgvector>=0.3.0
asyncpg>=0.30.0

# Document Processing
pypdf>=5.0.0
python-docx>=1.1.0
unstructured>=0.16.0
python-multipart>=0.0.20

# Utilities
python-dotenv>=1.0.0
httpx>=0.27.0
aiofiles>=24.0.0
```

### 4.6 Dependências Node.js (Frontend Vue.js)

```json
{
  "vue": "^3.5.0",
  "vue-router": "^4.5.0",
  "pinia": "^2.3.0",
  "tailwindcss": "^3.4.0",
  "@tailwindcss/typography": "^0.5.0",
  "lucide-vue-next": "^0.460.0",
  "marked": "^15.0.0",
  "axios": "^1.7.0",
  "@vueuse/core": "^12.0.0"
}
```

**Nota**: Frontend em dark mode exclusivo. Configuração Tailwind:
```js
// tailwind.config.js
module.exports = {
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Paleta dark mode
        background: '#0f172a',
        surface: '#1e293b',
        primary: '#3b82f6',
        secondary: '#64748b',
        text: '#f1f5f9',
        'text-muted': '#94a3b8'
      }
    }
  }
}
```

---

## 5. Project Type

**Web Application (SPA + API)**
- Backend: API RESTful FastAPI (Python 3.12.8)
- Frontend: Vue.js 3 SPA (Composition API) com dark mode
- Comunicação: HTTP REST + Server-Sent Events (SSE) para streaming
- Deployment: Local, com suporte a cloud em futuro
- LLM: OpenRouter API para POC (modelos free), Ollama opcional

---

## 6. Architecture Pattern

### 6.1 Pattern: Modular Monolith (Layered Architecture)

A arquitetura segue o padrão de Monolito Modular com separação clara de responsabilidades:

1. **Presentation Layer**: Interface web Vue.js 3 (dark mode)
2. **API Layer**: Endpoints FastAPI
3. **Service Layer**: Lógica de negócio (RAG, ingestão, chat)
4. **Data Layer**: PostgreSQL 18+ com pgvector (vetores e metadados unificados)
5. **Infrastructure Layer**: OpenRouter API, Ollama (opcional), processadores de documentos

### 6.2 Estrutura de Diretórios

```
local-rag/
├── backend/
│   ├── app/
│   │   ├── api/              # FastAPI routers
│   │   ├── core/             # Configurações e utilitários
│   │   ├── services/         # Lógica de negócio RAG
│   │   ├── models/           # SQLModel schemas (PostgreSQL)
│   │   └── infrastructure/   # Integrações externas (OpenRouter)
│   ├── tests/
│   ├── requirements.txt
│   └── main.py
├── frontend/
│   ├── src/
│   │   ├── components/       # Componentes Vue
│   │   │   ├── chat/
│   │   │   ├── documents/
│   │   │   └── common/
│   │   ├── views/           # Páginas/Views Vue
│   │   ├── stores/          # Pinia stores
│   │   ├── router/          # Vue Router config
│   │   ├── api/             # Clientes API (axios)
│   │   ├── composables/     # Composables Vue
│   │   ├── App.vue
│   │   └── main.js
│   ├── public/
│   ├── index.html
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── package.json
├── docs/
│   └── project/             # Documentação
├── data/                    # Persistência local
│   └── uploads/            # Documentos processados
├── sql/                    # Scripts PostgreSQL
│   ├── init.sql           # Schema inicial
│   └── migrations/        # Migrações
├── docker-compose.yml       # PostgreSQL + app
└── README.md
```
local-rag/
├── backend/
│   ├── app/
│   │   ├── api/              # FastAPI routers
│   │   ├── core/             # Configurações e utilitários
│   │   ├── services/         # Lógica de negócio RAG
│   │   ├── models/           # SQLModel schemas (PostgreSQL)
│   │   └── infrastructure/   # Integrações externas
│   ├── tests/
│   ├── requirements.txt
│   └── main.py
├── frontend/
│   ├── src/
│   │   ├── lib/
│   │   │   ├── components/   # Componentes Svelte
│   │   │   ├── stores/      # Svelte stores
│   │   │   └── api/         # Clientes API
│   │   ├── routes/          # Páginas SvelteKit
│   │   └── app.html
│   ├── static/
│   ├── tests/
│   └── package.json
├── docs/
│   └── project/             # Documentação
├── data/                    # Persistência local
│   └── uploads/            # Documentos processados
├── sql/                    # Scripts PostgreSQL
│   ├── init.sql           # Schema inicial
│   └── migrations/        # Migrações
├── docker-compose.yml       # PostgreSQL + app
└── README.md
```

---

## 7. Analysis of Alternatives

### 7.1 Backend Framework

| Approach | Pros | Cons |
|----------|------|------|
| **FastAPI (Chosen)** | Alta performance, async nativo, auto-documentação OpenAPI, excelente para streaming, integração Python nativa com LLM frameworks | Menos opções de templates/views que Django |
| Flask + Flask-SocketIO | Simples, flexível, boa para streaming | Requer mais boilerplate, menos performático |
| Django + DRF | Batteries included, admin pronto, robusto | Mais pesado, menos eficiente para streaming, curva de aprendizado |
| Do nothing | - | Impossibilita aplicação web |

**Chosen**: FastAPI
**Justification**: Melhor performance para APIs assíncronas com streaming de respostas LLM, integração nativa com Pydantic para validação, e ecossistema Python ideal para frameworks RAG.

### 7.2 RAG Framework

| Approach | Pros | Cons |
|----------|------|------|
| **LlamaIndex (Chosen)** | Especializado em RAG, ingestão de documentos robusta, abstrações claras, suporte nativo a ChromaDB e Ollama | Curva de aprendizado inicial |
| LangChain + LangGraph | Mais flexível, grande ecossistema, boa para agentes complexos | Mais verboso, pode ser overkill para RAG simples |
| Haystack | Boa arquitetura de pipelines, documentação clara | Menor ecossistema, menos integrações |
| Implementação customizada | Controle total | Alto esforço de desenvolvimento, manutenção complexa |
| Do nothing | - | Não entrega funcionalidade RAG |

**Chosen**: LlamaIndex
**Justification**: Framework especializado em RAG com APIs de alto nível para ingestão, indexação e recuperação, reduzindo código boilerplate e acelerando desenvolvimento.

### 7.3 Vector Database

| Approach | Pros | Cons |
|----------|------|------|
| ChromaDB | Embutido, zero-config, otimizado para local, integração nativa com LlamaIndex, persistência em arquivo | Menos escalável para clusters, dual database (vetores + SQLite separados) |
| FAISS | Muito rápido, GPU support, Facebook/Meta | Apenas índice, sem metadados nativos |
| **PostgreSQL + pgvector (Chosen)** | SQL completo, transações ACID, JOINs, backup unificado, HNSW/IVFFlat indexes, suporte a 16K dimensões | Requer instalação PostgreSQL 18+, setup inicial mais complexo |
| Milvus | Alto desempenho, cloud-native | Overkill para uso local simples |
| Pinecone | Managed, escalável | Cloud-only, custo, perde privacidade local |
| Do nothing | - | Impossibilita busca semântica |

**Chosen**: PostgreSQL 18+ com pgvector
**Justification**: Banco relacional robusto com extensão pgvector permite unificar vetores e metadados em uma única fonte de dados, aproveitando ACID compliance, backups consistentes, e índices HNSW para busca vetorial de alta performance. Elimina necessidade de manter dois bancos (ChromaDB + SQLite).

### 7.4 LLM Provider (POC)

| Approach | Pros | Cons |
|----------|------|------|
| **OpenRouter API (Chosen for POC)** | Acesso a modelos free, API unificada, sem necessidade de hardware local, rate limits generosos para free | Requer conexão internet, rate limits aplicáveis |
| Ollama Local | 100% offline, privacidade total, sem rate limits | Requer GPU potente, setup inicial complexo |
| llama.cpp | Muito eficiente em CPU, leve, portátil | Menos otimizado, API menos conveniente |
| text-generation-inference (TGI) | Alto throughput, otimizado | Complexo de configurar, primariamente NVIDIA |

**Chosen for POC**: OpenRouter API
**Justification**: Para a POC, usar modelos free via OpenRouter elimina a necessidade de hardware GPU específico e permite desenvolvimento e testes imediatos. A arquitetura suporta fácil migração para Ollama local em produção.
### 7.5 Frontend Framework

| Approach | Pros | Cons |
|----------|------|------|
| SvelteKit | Performance excelente, menos boilerplate, reatividade nativa | Ecossistema menor que Vue/React |
| React + Next.js | Ecossistema enorme, muitos componentes prontos | Mais pesado, mais complexo |
| **Vue 3 (Chosen)** | Composition API poderoso, Pinia state management, excelente DX, dark mode fácil, ecossistema maduro | Curva de aprendizado inicial (moderada) |
| HTMX + Server-side | Ultra simples, sem JS framework | Menos interativo, requer mais roundtrips |
| Do nothing | - | Sem interface web |

**Chosen**: Vue.js 3 (Composition API)
**Justification**: Vue 3 oferece excelente equilíbrio entre produtividade e performance, com Composition API para lógica reutilizável, Pinia para gerenciamento de estado, e suporte nativo a dark mode via TailwindCSS. Ecossistema maduro com Vue Router e excelente documentação.

---

## 8. Solution Design (Mermaid Diagram)

### 8.1 Arquitetura Geral

```mermaid
flowchart TB
    subgraph "Frontend (Vue.js 3)"
        UI[Interface Web<br/>Dark Mode]
        Chat[Chat Component]
        Docs[Document Manager]
        Auth[Auth Local POC]
    end

    subgraph "Backend (FastAPI)"
        API[REST API]
        RAG[RAG Service]
        Ingest[Ingestion Service]
        SSE[Server-Sent Events]
    end

    subgraph "RAG Pipeline"
        Loader[Document Loaders]
        Splitter[Text Splitters]
        Embed[Embedding Model<br/>OpenRouter]
        Index[Vector Index]
        Retriever[Retriever]
        LLM[LLM Interface<br/>OpenRouter]
    end

    subgraph "Storage"
        Postgres[(PostgreSQL 18+<br/>pgvector)]
        Files[Uploads/Cache]
    end

    subgraph "AI Infrastructure"
        OpenRouter[OpenRouter API<br/>Modelos Free]
        Ollama[Ollama Local<br/>Opcional/Futuro]
    end

    UI --> API
    Chat --> SSE
    Docs --> API
    API --> RAG
    API --> Ingest
    
    RAG --> Retriever
    RAG --> LLM
    Ingest --> Loader
    Loader --> Splitter
    Splitter --> Embed
    Embed --> Index
    
    Index --> Postgres
    Retriever --> Postgres
    LLM --> OpenRouter
    Embed --> OpenRouter
    
    Loader --> Files
```

### 8.2 Fluxo de Ingestão de Documentos

```mermaid
flowchart LR
    A[Upload<br/>PDF/DOCX/TXT] --> B{Validação}
    B -->|Inválido| C[Erro: Formato não suportado]
    B -->|Válido| D[Document Loader]
    D --> E[Text Splitter<br/>Chunking]
    E --> F[Geração de Embeddings]
    F --> G[PostgreSQL + pgvector<br/>Indexação]
    G --> H[Metadados + Vetores<br/>Unificados]
    H --> I[Confirmação]
```

### 8.3 Fluxo de Chat/Query

```mermaid
flowchart LR
    A[Pergunta do Usuário] --> B[Query Embedding]
    B --> C[Busca Vetorial<br/>pgvector HNSW]
    C --> D[Recuperação Top-K]
    D --> E[Context Assembly]
    E --> F[Prompt com Contexto]
    F --> G[Ollama LLM<br/>Streaming]
    G --> H[Resposta + Fontes]
```

---

## 9. Data Architecture

### 9.1 PostgreSQL + pgvector Schema (Unified Storage)

**Habilitar extensão pgvector:**
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### 9.2 Schema Completo

```sql
-- Users
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user' CHECK (role IN ('admin', 'user')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Documents (metadados dos arquivos)
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT,
    file_type VARCHAR(50),
    total_chunks INTEGER,
    uploaded_by INTEGER,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'processing', 'error')),
    FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE CASCADE
);

-- Document Chunks (vetores + conteúdo)
CREATE TABLE document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id INTEGER NOT NULL,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    embedding vector(768),  -- nomic-embed-text = 768 dimensões
    page_number INTEGER,
    uploaded_by INTEGER,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
    FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE CASCADE
);

-- Índice HNSW para busca vetorial de alta performance
CREATE INDEX ON document_chunks 
USING hnsw (embedding vector_cosine_ops) 
WITH (m = 16, ef_construction = 64);

-- Índice para busca por documento
CREATE INDEX idx_document_chunks_document_id ON document_chunks(document_id);

-- Chat Sessions
CREATE TABLE chat_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    title VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Chat Messages
CREATE TABLE chat_messages (
    id SERIAL PRIMARY KEY,
    session_id INTEGER,
    role VARCHAR(20) CHECK (role IN ('user', 'assistant')),
    content TEXT,
    sources JSONB,  -- Array de referências aos chunks usados
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE
);

-- System Config
CREATE TABLE system_config (
    key VARCHAR(100) PRIMARY KEY,
    value TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices adicionais para performance
CREATE INDEX idx_documents_uploaded_by ON documents(uploaded_by);
CREATE INDEX idx_chat_sessions_user_id ON chat_sessions(user_id);
CREATE INDEX idx_chat_messages_session_id ON chat_messages(session_id);
```

### 9.3 Configurações Padrão

```sql
-- Inserir configurações iniciais (POC)
INSERT INTO system_config (key, value) VALUES
('llm_provider', 'openrouter'),
('llm_model', 'meta-llama/llama-3.2-3b-instruct:free'),
('llm_model_local', 'llama3.2'),
('embedding_model', 'sentence-transformers/all-MiniLM-L6-v2'),
('chunk_size', '512'),
('chunk_overlap', '50'),
('top_k_retrieval', '5'),
('temperature', '0.7'),
('max_tokens', '2048'),
('system_prompt', 'Você é um assistente útil que responde com base nos documentos fornecidos. Cite as fontes usadas.'),
('hnsw_m', '16'),
('hnsw_ef_construction', '64'),
('hnsw_ef_search', '100');

-- Inserir usuário padrão POC (1 usuário apenas)
-- localuser / localuser123
-- [SUPOSIÇÃO]: Autenticação multi-user via Google SSO/Auth0 será funcionalidade futura
INSERT INTO users (username, hashed_password, role) VALUES
('localuser', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiAYMyzJ/Iy', 'admin');
```

---

## 10. Integrações e Dependências Externas

### 10.1 Dependências de Sistema

| Pacote | Versão | Finalidade |
|--------|--------|------------|
| PostgreSQL | 18+ | Banco de dados principal com vetores |
| pgvector | 0.8.x+ | Extensão para vetores no PostgreSQL |
| Python | 3.12.8 | Ambiente de execução |
| Node.js | 20.x+ | Ambiente frontend |
| OpenRouter Account | - | API key para modelos free |

**Opcional/Futuro:**
| Pacote | Versão | Finalidade |
|--------|--------|------------|
| ROCm | 6.2+ | Stack GPU AMD (para Ollama local) |
| Ollama | 0.5.x+ | Runtime LLM local (opcional) |

### 10.2 Modelos OpenRouter (POC - Free Tier)

Não é necessário instalação local. Basta criar conta em [openrouter.ai](https://openrouter.ai) e obter API key.

Modelos free disponíveis via OpenRouter:
- `meta-llama/llama-3.2-3b-instruct:free`
- `mistralai/mistral-7b-instruct:free`
- `deepseek/deepseek-chat:free`
- `google/gemma-2-9b-it:free`

### 10.3 Modelos Ollama (Opcional/Futuro)

```bash
# Apenas se optar por modo local no futuro
ollama pull llama3.2
ollama pull nomic-embed-text

# Opcional
ollama pull mistral
ollama pull bge-m3
```

---

## 11. Configuração de Ambiente

### 11.1 Variáveis de Ambiente (.env)

```bash
# API
APP_NAME=LocalRAG
DEBUG=false
API_HOST=0.0.0.0
API_PORT=8000

# Database
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/localrag
PGVECTOR_DIMS=384  # all-MiniLM-L6-v2 = 384 dimensões

# LLM Provider (POC: openrouter)
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=your-openrouter-api-key
OPENROUTER_MODEL=meta-llama/llama-3.2-3b-instruct:free
OPENROUTER_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Ollama (opcional/futuro)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_LLM_MODEL=llama3.2
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

# RAG Settings
CHUNK_SIZE=512
CHUNK_OVERLAP=50
TOP_K=5
TEMPERATURE=0.7
MAX_TOKENS=2048

# Storage
UPLOAD_DIR=./data/uploads
MAX_FILE_SIZE=100MB
ALLOWED_EXTENSIONS=pdf,txt,docx,md

# Security
SECRET_KEY=your-secret-key-here-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### 11.2 Comandos de Inicialização

```bash
# PostgreSQL (se não usando Docker)
sudo systemctl start postgresql

# Backend
cd backend
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend (Vue.js)
cd frontend
npm install
npm run dev

# Ollama (opcional/futuro)
# ollama serve
```

---

## 12. Considerações de Performance e Hardware

### 12.1 POC (Qualquer Hardware)

Para a POC usando OpenRouter API, não há requisitos de GPU:

| Componente | Requisito |
|------------|-----------|
| CPU | Qualquer processador moderno (4+ cores) |
| RAM | 8GB mínimo, 16GB recomendado |
| Disco | 10GB+ para PostgreSQL e documentos |
| Rede | Conexão internet estável |
| GPU | **Não necessário** |

### 12.2 Produção com Ollama Local (Opcional/Futuro)

Se migrar para Ollama local no futuro:

| Componente | VRAM Estimada |
|------------|---------------|
| llama3.2 (3B) | ~2.5GB |
| nomic-embed-text | ~400MB |
| ROCm overhead | ~500MB |
| Margem de segurança | ~2GB |
| **Total** | **~5.5GB / 16GB disponível** |

### 12.3 Capacidade de Processamento

- **Contexto máximo**: 128K tokens (OpenRouter)
- **Throughput ingestão**: ~10-20 documentos/minuto
- **Latência query**: 1-5 segundos (depende do modelo OpenRouter)
- **Capacidade do banco**: Suporte a milhões de chunks com HNSW index

### 12.4 Otimizações (Modo Local Futuro)

- ROCm 6.2+ para suporte RDNA3
- Flash Attention 2 quando disponível para AMD
- Quantização Q4_0 para modelos maiores

---

## 13. Segurança e Privacidade

### 13.1 Medidas de Segurança (POC)

- Dados dos documentos armazenados localmente (PostgreSQL)
- Sanitização de uploads
- Isolamento de processamento de documentos
- 1 usuário local simples (senha hasheada)
- Comunicação OpenRouter apenas para queries LLM

### 13.2 Limitações Intencionais

- POC requer conexão à internet (OpenRouter API)
- Sem sincronização cloud de documentos
- Sem compartilhamento automático
- Logs locais apenas

### 13.3 Segurança Futura (Google SSO/Auth0)

**[FUNCIONALIDADE FUTURA]** Autenticação via Google SSO usando Auth0:
- Login seguro com conta Google
- Gestão de múltiplos usuários
- Controle de acesso por roles
- Tokens JWT para sessões
- Proteção de rotas da API

---

## 14. Planos Futuros (Não MVP)

1. Suporte a multimodal (imagens via llava)
2. Sistema de plugins para novos formatos
3. Fine-tuning local leve
4. Exportação/importação de collections
5. Interface CLI opcional

---

## 15. Instalação PostgreSQL 18 + pgvector

### 15.1 CachyOS / Arch Linux

```bash
# Instalar PostgreSQL 18
sudo pacman -S postgresql

# Inicializar cluster
sudo -iu postgres initdb -D /var/lib/postgres/data --locale=en_US.UTF-8

# Instalar pgvector
# Compilar a partir do fonte
cd /tmp
git clone --branch v0.8.2 https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install

# Iniciar PostgreSQL
sudo systemctl enable --now postgresql

# Criar banco e usuário
sudo -iu postgres psql -c "CREATE USER localrag WITH PASSWORD 'sua_senha';"
sudo -iu postgres psql -c "CREATE DATABASE localrag OWNER localrag;"
sudo -iu postgres psql -d localrag -c "CREATE EXTENSION IF NOT EXISTS vector;"
sudo -iu postgres psql -d localrag -c "CREATE EXTENSION IF NOT EXISTS pgcrypto;"
```

### 15.2 Docker (Alternativa Rápida)

```bash
# Usar imagem oficial com pgvector
sudo docker run -d \
  --name localrag-postgres \
  -e POSTGRES_USER=localrag \
  -e POSTGRES_PASSWORD=sua_senha \
  -e POSTGRES_DB=localrag \
  -v localrag_data:/var/lib/postgresql/data \
  -p 5432:5432 \
  pgvector/pgvector:pg18
```

### 15.3 Configurações PostgreSQL Recomendadas

Editar `/var/lib/postgres/data/postgresql.conf`:

```conf
# Memória
shared_buffers = 8GB                    # 25% da RAM
effective_cache_size = 24GB             # 75% da RAM
work_mem = 256MB                      # Para ordenações
maintenance_work_mem = 2GB             # Para indexação

# Conexões
max_connections = 100

# Performance
random_page_cost = 1.1                 # Para SSD/NVMe
effective_io_concurrency = 200

# Logging
log_min_duration_statement = 1000       # Log queries > 1s
log_checkpoints = on
log_connections = on
```

---

## 16. Referências

- [LlamaIndex Documentation](https://docs.llamaindex.ai)
- [LangChain Integrations](https://python.langchain.com/docs/integrations/providers/)
- [OpenRouter Documentation](https://openrouter.ai/docs)
- [OpenRouter Free Models](https://openrouter.ai/docs/guides/routing/model-variants/free)
- [Ollama AMD Support](https://ollama.com/blog/amd-preview)
- [AMD ROCm Documentation](https://rocm.docs.amd.com)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Vue.js 3 Documentation](https://vuejs.org/guide/introduction)
- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [PostgreSQL 18 Release Notes](https://www.postgresql.org/docs/18/release-18.html)

---

**Changelog v1.2**:
- POC simplificada: 1 usuário local (multi-user via Google SSO/Auth0 é funcionalidade futura)
- Backend atualizado: Python 3.12.8, FastAPI latest
- Frontend alterado: Vue.js 3 (Composition API) com dark mode exclusivo
- Suporte dual para LLM: OpenRouter API (modelos free) + Ollama local opcional
- Removida restrição de hardware AMD - POC funciona em qualquer hardware
- Removido SvelteKit (replaced by Vue.js)

**Documento gerado em**: 19/04/2026
**Próximos passos**: Revisão de especificação técnica e início de implementação
