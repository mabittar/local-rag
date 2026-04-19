# Local RAG Platform - Frontend

Frontend Vue.js 3 para POC de plataforma RAG com dark mode exclusivo.

## Stack

- **Vue 3** - Composition API
- **Vite** - Build tool
- **TailwindCSS** - Dark mode styling
- **Pinia** - State management
- **Vue Router** - Client-side routing
- **Axios** - HTTP client
- **Lucide Vue** - Icons
- **Marked** - Markdown rendering

## Setup

```bash
cd frontend
npm install
npm run dev
```

Acesse http://localhost:5173

## Estrutura

```
src/
├── components/
│   ├── layout/      # AppLayout, Sidebar, Header
│   ├── chat/        # Chat components
│   └── documents/   # Document components
├── views/
│   ├── LoginView.vue
│   ├── ChatView.vue
│   └── DocumentsView.vue
├── stores/
│   ├── auth.js      # Auth store
│   ├── chat.js      # Chat store + SSE
│   └── documents.js # Documents store
├── router/
│   └── index.js     # Route config
├── api/
│   └── axios.js     # HTTP client
└── composables/
    └── use*.js      # Reusable composables
```

## Credenciais

- **Usuário**: localuser
- **Senha**: localuser123

## Features

- Dark mode exclusivo
- Chat com streaming SSE
- Upload drag-and-drop
- Gestão de documentos
- Autenticação JWT

## Build

```bash
npm run build
```
