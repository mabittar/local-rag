<template>
  <div class="min-h-screen bg-background flex items-center justify-center">
    <div class="w-full max-w-md">
      <div class="text-center mb-8">
        <div class="inline-flex items-center justify-center w-16 h-16 rounded-xl bg-primary mb-4">
          <MessageSquare class="w-8 h-8 text-white" />
        </div>
        <h1 class="text-2xl font-bold text-text">Local RAG Platform</h1>
        <p class="text-text-muted mt-2">Faça login para continuar</p>
      </div>
      
      <form @submit.prevent="handleLogin" class="bg-surface rounded-xl border border-border p-8 space-y-6">
        <div v-if="error" data-testid="login-error" class="p-4 bg-error/10 border border-error/20 rounded-lg text-error text-sm">
          Erro ao fazer login: {{ error }}
        </div>
        
        <div>
          <label class="block text-sm font-medium text-text mb-2">Usuário</label>
          <input
            v-model="credentials.username"
            type="text"
            required
            class="w-full px-4 py-3 bg-background border border-border rounded-lg text-text placeholder-text-muted focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors"
            placeholder="localuser"
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-text mb-2">Senha</label>
          <input
            v-model="credentials.password"
            type="password"
            required
            class="w-full px-4 py-3 bg-background border border-border rounded-lg text-text placeholder-text-muted focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors"
            placeholder="••••••••"
          />
        </div>
        
        <button
          type="submit"
          :disabled="isLoading"
          class="w-full py-3 px-4 bg-primary hover:bg-primary-hover disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors flex items-center justify-center gap-2"
        >
          <Loader2 v-if="isLoading" class="w-5 h-5 animate-spin" />
          <span>{{ isLoading ? 'Entrando...' : 'Entrar' }}</span>
        </button>
      </form>
      
      <p class="text-center text-text-muted text-sm mt-6">
        Use as credenciais: localuser / localuser123
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { MessageSquare, Loader2 } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

const credentials = reactive({
  username: '',
  password: '',
})

const isLoading = ref(false)
const error = ref('')

async function handleLogin() {
  isLoading.value = true
  error.value = ''
  
  try {
    await auth.login(credentials)
    router.push('/chat')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Erro ao fazer login. Tente novamente.'
  } finally {
    isLoading.value = false
  }
}
</script>
