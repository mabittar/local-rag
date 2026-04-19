<template>
  <header class="h-16 bg-surface border-b border-border flex items-center justify-between px-6">
    <h2 class="text-lg font-semibold text-text">
      {{ pageTitle }}
    </h2>
    
    <div class="flex items-center gap-4">
      <span class="text-sm text-text-muted">
        {{ auth.isAuthenticated ? 'Conectado' : 'Desconectado' }}
      </span>
      <div class="w-8 h-8 rounded-full bg-primary flex items-center justify-center">
        <User class="w-4 h-4 text-white" />
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { User } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const auth = useAuthStore()

const pageTitle = computed(() => {
  switch (route.path) {
    case '/chat':
      return 'Chat com RAG'
    case '/documents':
      return 'Gerenciamento de Documentos'
    default:
      return 'Local RAG Platform'
  }
})
</script>
