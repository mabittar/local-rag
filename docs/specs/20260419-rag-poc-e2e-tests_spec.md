# POC RAG Platform - E2E Tests Specification

**Date**: 19/04/2026
**Last Update**: 19/04/2026
**Version**: 1.0
**Requester**: Local RAG Platform POC
**Priority**: 🔴 HIGH

**Changelog v1.0**:
- Initial specification for E2E tests using Playwright
- Full stack integration: Frontend + Backend + Database
- End-to-end coverage of critical user flows

---

## Objective

Implementar testes end-to-end (E2E) para a plataforma RAG usando Playwright, garantindo que todos os fluxos críticos funcionem corretamente do frontend ao backend e banco de dados. Os testes devem validar a integração completa da aplicação, incluindo autenticação, upload de documentos, e chat com streaming RAG.

---

## Functional Description

A suite de testes E2E cobre:
1. **Autenticação**: Login com credenciais válidas/inválidas
2. **Upload de Documentos**: Drag-and-drop e input file
3. **Chat com RAG**: Envio de mensagens e streaming de respostas
4. **Gestão de Sessões**: Criar, listar e excluir sessões de chat
5. **Integração Full-Stack**: Frontend Vue.js -> Backend FastAPI -> PostgreSQL

Os testes utilizam Playwright com browser headless, executando em ambiente controlado com banco de dados de teste isolado.

---

## Technical Flow

### Test Setup Flow
1. **Trigger**: Início da execução dos testes
2. **Validation**: Verificar se containers Docker (PostgreSQL, Backend) estão rodando
3. **Processing**: 
   - Limpar e recriar banco de dados de teste
   - Inserir seed data (usuário localuser)
   - Iniciar aplicação frontend em modo teste
4. **Persistence**: Dados de teste isolados em PostgreSQL
5. **Response**: Suite de testes executa em sequência

### Test Execution Flow
1. **Trigger**: Playwright executa teste específico
2. **Validation**: Verificar estado inicial da aplicação
3. **Processing**: 
   - Navegar para página
   - Interagir com elementos (click, type, drag-drop)
   - Aguardar respostas do backend
   - Verificar SSE streaming
4. **Persistence**: Dados persistem no banco PostgreSQL
5. **Response**: Asserções sobre UI e dados

---

## Acceptance Criteria

### Feature: Authentication E2E
**Effort**: Low | **Risk**: Low

#### Scenario: Success - Login with valid credentials
Given que o usuário acessa a página de login
And o backend está rodando com seed data
When digita "localuser" no campo username
And digita "localuser123" no campo password
And clica no botão "Entrar"
Then o sistema redireciona para /chat
And o token JWT está armazenado no localStorage
And a sidebar mostra "Conectado"

#### Scenario: Error - Login with invalid credentials
Given que o usuário está na página de login
When digita credenciais inválidas
And clica em "Entrar"
Then o sistema mostra mensagem "Erro ao fazer login"
And permanece na página de login

### Feature: Document Upload E2E
**Effort**: Medium | **Risk**: Medium

#### Scenario: Success - Upload valid document
Given que o usuário está autenticado
And navegou para /documents
When arrasta um arquivo test.txt para a área de drop
Then o upload inicia automaticamente
And a barra de progresso aparece
And ao completar, o documento aparece na lista
And o status é "completed"

#### Scenario: Error - Upload invalid file type
Given que o usuário está na página de documentos
When tenta uploadar arquivo .exe
Then o sistema mostra erro "Formato não suportado"
And o upload não inicia

### Feature: Chat E2E
**Effort**: High | **Risk**: Medium

#### Scenario: Success - Send message and receive streaming response
Given que o usuário está autenticado
And tem documentos indexados
And está na página de chat
When cria uma nova sessão
And digita "Resuma meus documentos" e pressiona Enter
Then a mensagem aparece na conversa
And o indicador "Pensando..." aparece
And a resposta é renderizada token por token
And ao finalizar, o botão "Ver fontes" aparece

#### Scenario: Success - View chat history
Given que o usuário tem múltiplas conversas
When clica em uma sessão antiga na sidebar
Then o histórico da conversa é carregado
And as mensagens anteriores são exibidas

#### Scenario: Error - API unavailable during chat
Given que o usuário enviou uma mensagem
When a conexão com o backend é perdida
Then o sistema mostra "Conexão perdida"
And após 3 tentativas, mostra "Erro ao receber resposta"

### Feature: Database Integration E2E
**Effort**: Medium | **Risk**: Low

#### Scenario: Success - Data persists correctly
Given que o usuário faz upload de documento
When consulta o banco PostgreSQL
Then o documento está na tabela documents
And os chunks estão na tabela document_chunks
And os embeddings foram gerados

#### Scenario: Success - Cascade delete works
Given que o usuário exclui um documento
When verifica o banco
Then o documento foi removido da tabela documents
And todos os chunks relacionados foram removidos

---

## Technical Considerations

### Test Framework
- **Playwright**: Testes E2E com suporte a browsers headless
- **@playwright/test**: Test runner integrado
- **expect**: Asserções built-in

### Project Structure
```
e2e-tests/
├── playwright.config.js       # Configuração do Playwright
├── package.json               # Dependências
├── tests/
│   ├── auth.spec.js          # Testes de autenticação
│   ├── documents.spec.js     # Testes de documentos
│   ├── chat.spec.js          # Testes de chat
│   └── setup/
│       └── global-setup.js   # Setup global (seed DB)
├── fixtures/
│   ├── test-document.txt     # Arquivos para upload
│   └── test-document.pdf
└── .env.test                 # Variáveis de ambiente
```

### Test Database
- **URL**: postgresql+asyncpg://localrag:localrag123@localhost:5433/localrag_test
- **Strategy**: Recreate before each test suite
- **Seed**: Usuário localuser + documentos de teste

### Configuration

```javascript
// playwright.config.js
module.exports = {
  testDir: './tests',
  fullyParallel: false, // E2E tests should run sequentially
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: 1, // Database tests need sequential execution
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:5173',
    trace: 'on-first-retry',
    headless: true,
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  webServer: {
    command: 'cd ../frontend && npm run dev',
    port: 5173,
    reuseExistingServer: !process.env.CI,
  },
};
```

### Dependencies

```json
{
  "devDependencies": {
    "@playwright/test": "^1.40.0",
    "pg": "^8.11.0"
  }
}
```

### Security
- **Environment Variables**: DATABASE_URL_TEST, API_URL
- **Isolated DB**: Banco de dados separado para testes
- **Test Credentials**: localuser / localuser123 (mesmas do dev)

### Observability
- **Screenshots**: On failure
- **Videos**: Retain on failure
- **Traces**: On first retry
- **Console Logs**: Captured

---

## Solution Design (Mermaid Diagram)

### E2E Test Architecture

```mermaid
flowchart TB
    subgraph "Playwright Test Suite"
        PW[Playwright Test Runner]
        Auth[auth.spec.js]
        Docs[documents.spec.js]
        Chat[chat.spec.js]
        Setup[global-setup.js]
    end

    subgraph "Test Infrastructure"
        Browser[Chromium Headless]
        Page[Page Object]
    end

    subgraph "Application Under Test"
        Frontend[Vue.js 3 Frontend<br/>localhost:5173]
        Backend[FastAPI Backend<br/>localhost:8000]
        Database[PostgreSQL Test DB<br/>localhost:5433]
    end

    PW --> Auth
    PW --> Docs
    PW --> Chat
    Setup --> Database
    
    Auth --> Page
    Docs --> Page
    Chat --> Page
    
    Page --> Browser
    Browser --> Frontend
    Frontend --> Backend
    Backend --> Database
```

### Test Data Flow

```mermaid
sequenceDiagram
    participant Test as Playwright Test
    participant DB as PostgreSQL
    participant API as FastAPI
    participant UI as Vue.js Frontend
    participant User as User Actions

    Test->>DB: Clean database
    Test->>DB: Seed test data
    Test->>UI: Navigate to /login
    User->>UI: Type credentials
    User->>UI: Click login
    UI->>API: POST /api/auth/login
    API->>DB: Validate user
    DB-->>API: User data
    API-->>UI: JWT token
    UI-->>Test: Redirect to /chat
    Test->>UI: Verify logged in
```

### Document Upload Test Flow

```mermaid
sequenceDiagram
    participant Test as Playwright Test
    participant UI as Vue.js
    participant API as FastAPI
    participant DB as PostgreSQL
    participant FS as File System

    Test->>UI: Navigate to /documents
    Test->>UI: Drag file to dropzone
    UI->>API: POST /api/documents/upload
    API->>FS: Save file
    API->>API: Extract text & chunk
    API->>API: Generate embeddings
    API->>DB: Insert document + chunks
    API-->>UI: Upload complete
    UI-->>Test: Document in list
    Test->>DB: Verify document exists
    Test->>DB: Verify chunks exist
```

---

## Definition of Done

- [ ] Playwright configurado e rodando
- [ ] Testes de autenticação passando
- [ ] Testes de upload de documentos passando
- [ ] Testes de chat com streaming passando
- [ ] Testes de banco de dados passando
- [ ] Screenshots/Videos em caso de falha
- [ ] CI/CD integration ready
- [ ] Documentação de execução

---

## Verification Checklist

- [ ] Database isolation working
- [ ] Tests are independent and atomic
- [ ] Critical paths covered
- [ ] Headless execution working
- [ ] Retry mechanism configured
- [ ] Artifacts on failure (screenshots, videos)

---

## Next Step

Após aprovação, execute `/plan` para gerar o plano de implementação detalhado.
