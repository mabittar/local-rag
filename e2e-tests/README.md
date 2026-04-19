# Local RAG Platform - E2E Tests

Testes end-to-end usando Playwright para validação da aplicação completa.

## Stack

- **Playwright**: Framework de testes E2E
- **pg**: Cliente PostgreSQL para setup/teardown
- **Chromium**: Browser headless para testes

## Setup

```bash
cd e2e-tests
npm install
npx playwright install chromium
```

## Configuração

Copie `.env.test.example` para `.env.test` e ajuste as variáveis:

```env
FRONTEND_URL=http://localhost:5173
API_URL=http://localhost:8000
DATABASE_URL=postgresql://localrag:localrag123@localhost:5433/localrag_test
TEST_USER_USERNAME=localuser
TEST_USER_PASSWORD=localuser123
```

## Executando Testes

```bash
# Todos os testes
npx playwright test

# Com interface visual
npx playwright test --ui

# Modo debug
npx playwright test --debug

# Apenas autenticação
npx playwright test auth.spec.js

# Apenas documentos
npx playwright test documents.spec.js

# Apenas chat
npx playwright test chat.spec.js
```

## Estrutura

```
e2e-tests/
├── fixtures/              # Arquivos para upload
│   ├── test-document.txt
│   └── test-document.md
├── tests/
│   ├── auth.spec.js      # Testes de autenticação
│   ├── documents.spec.js # Testes de documentos
│   ├── chat.spec.js      # Testes de chat
│   └── setup/
│       ├── global-setup.js    # Seed database
│       └── global-teardown.js # Clean database
├── utils/
│   └── test-helpers.js   # Funções auxiliares
├── playwright.config.js # Configuração
└── .env.test            # Variáveis de ambiente
```

## Testes Implementados

### Autenticação (auth.spec.js)
- Login com credenciais válidas
- Login com credenciais inválidas

### Documentos (documents.spec.js)
- Upload de arquivo válido
- Upload de arquivo inválido
- Exclusão de documento

### Chat (chat.spec.js)
- Criar nova sessão
- Enviar mensagem
- Visualizar histórico
- Excluir sessão

## CI/CD

```bash
# Executar em CI
CI=true npx playwright test
```

## Debugging

Screenshots e videos são salvos automaticamente em caso de falha:

- `test-results/`: Screenshots, videos, traces
- Relatório HTML: `npx playwright show-report`

## Requisitos

- Node.js 20+
- Backend rodando em localhost:8000
- Frontend rodando em localhost:5173
- PostgreSQL com banco localrag_test

## Troubleshooting

### Browser não encontrado
```bash
npx playwright install --force chromium
```

### Database connection error
Verifique se o PostgreSQL está rodando e o banco localrag_test existe.

### Testes falhando intermitentemente
Aumente os timeouts no playwright.config.js ou use `--retries=2`.
