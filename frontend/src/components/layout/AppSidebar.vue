<template>
  <aside class="w-64 bg-surface border-r border-border flex flex-col">
    <div class="p-6 border-b border-border">
      <h1 class="text-xl font-bold text-text flex items-center gap-2">
        <MessageSquare class="w-6 h-6 text-primary" />
        Local RAG
      </h1>
      <p class="text-xs text-text-muted mt-1">POC Platform</p>
    </div>
    
    <nav class="flex-1 p-4 space-y-2">
      <RouterLink
        to="/chat"
        :class="[
          'flex items-center gap-3 px-4 py-3 rounded-lg transition-colors',
          route.path === '/chat'
            ? 'bg-primary text-white'
            : 'text-text-muted hover:bg-surface-hover hover:text-text',
        ]"
      >
        <MessageSquare class="w-5 h-5" />
        <span>Chat</span>
      </RouterLink>
      
      <RouterLink
        to="/documents"
        :class="[
          'flex items-center gap-3 px-4 py-3 rounded-lg transition-colors',
          route.path === '/documents'
            ? 'bg-primary text-white'
            : 'text-text-muted hover:bg-surface-hover hover:text-text',
        ]"
      >
        <FileText class="w-5 h-5" />
        <span>Documentos</span>
      </RouterLink>
    </nav>
    
    <div class="p-4 border-t border-border">
      <button
        @click="logout"
        class="w-full flex items-center gap-3 px-4 py-3 text-text-muted hover:text-error transition-colors"
      >
        <LogOut class="w-5 h-5" />
        <span>Sair</span>
      </button>
    </div>
  </aside>
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router'
import { MessageSquare, FileText, LogOut } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

function logout() {
  auth.logout()
  router.push('/login')
}
</script>
