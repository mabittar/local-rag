<template>
  <div class="h-full flex">
    <!-- Chat Sidebar -->
    <div class="w-64 bg-surface border-r border-border flex flex-col">
      <div class="p-4 border-b border-border">
        <button
          @click="createNewSession"
          class="w-full flex items-center justify-center gap-2 py-2 px-4 bg-primary hover:bg-primary-hover text-white rounded-lg transition-colors"
        >
          <Plus class="w-4 h-4" />
          <span>Nova Conversa</span>
        </button>
      </div>
      
      <div class="flex-1 overflow-y-auto p-4 space-y-2">
<div
      v-for="session in chatStore.sessions"
      :key="session.id"
      data-testid="chat-session"
      @click="selectSession(session)"
      :class="[
            'p-3 rounded-lg cursor-pointer transition-colors group',
            chatStore.currentSession?.id === session.id
              ? 'bg-primary/20 border border-primary/30'
              : 'hover:bg-surface-hover border border-transparent',
          ]"
        >
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2 flex-1 min-w-0">
              <MessageSquare class="w-4 h-4 text-text-muted flex-shrink-0" />
              <span class="text-sm text-text truncate">
                {{ session.title || 'Nova Conversa' }}
              </span>
            </div>
<button
            @click.stop="deleteSession(session.id)"
            data-testid="delete-session"
            class="opacity-0 group-hover:opacity-100 p-1 hover:bg-error/20 rounded transition-all"
          >
              <Trash2 class="w-4 h-4 text-error" />
            </button>
          </div>
          <p class="text-xs text-text-muted mt-1">
            {{ formatDate(session.created_at) }}
          </p>
        </div>
      </div>
    </div>
    
    <!-- Chat Area -->
    <div class="flex-1 flex flex-col chat-container" data-testid="chat-container">
      <!-- Messages -->
      <div ref="messagesContainer" class="flex-1 overflow-y-auto p-6 space-y-6">
        <div v-if="chatStore.messages.length === 0" class="text-center py-20">
          <MessageSquare class="w-12 h-12 text-text-muted mx-auto mb-4" />
          <p class="text-text-muted">Inicie uma conversa sobre seus documentos</p>
        </div>
        
        <template v-for="message in chatStore.messages" :key="message.id">
          <!-- User Message -->
          <div v-if="message.role === 'user'" class="flex justify-end">
            <div class="max-w-2xl bg-primary text-white px-6 py-4 rounded-2xl rounded-tr-sm">
              <p class="whitespace-pre-wrap">{{ message.content }}</p>
            </div>
          </div>
          
          <!-- Assistant Message -->
          <div v-else class="flex">
            <div class="max-w-3xl bg-surface border border-border px-6 py-4 rounded-2xl rounded-tl-sm">
              <div class="markdown-content" v-html="renderMarkdown(message.content)"></div>
              
              <button
                v-if="message.sources?.length"
                @click="showSources(message.sources)"
                class="mt-3 text-sm text-primary hover:underline flex items-center gap-1"
              >
                <BookOpen class="w-4 h-4" />
                {{ message.sources.length }} fonte(s)
              </button>
            </div>
          </div>
        </template>
        
        <!-- Streaming Message -->
        <div v-if="chatStore.isStreaming" class="flex">
          <div class="max-w-3xl bg-surface border border-border px-6 py-4 rounded-2xl rounded-tl-sm">
            <div class="markdown-content" v-html="renderMarkdown(chatStore.streamingContent)"></div>
            <div class="mt-2 flex items-center gap-2 text-text-muted">
              <Loader2 class="w-4 h-4 animate-spin" />
              <span class="text-sm">Pensando...</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Input Area -->
      <div class="border-t border-border p-4">
        <form @submit.prevent="sendMessage" class="max-w-4xl mx-auto flex gap-4">
          <input
            v-model="messageInput"
            type="text"
            placeholder="Digite sua mensagem..."
            :disabled="chatStore.isStreaming"
            class="flex-1 px-4 py-3 bg-background border border-border rounded-lg text-text placeholder-text-muted focus:outline-none focus:border-primary transition-colors"
          />
          <button
            type="submit"
            :disabled="!messageInput.trim() || chatStore.isStreaming"
            class="px-6 py-3 bg-primary hover:bg-primary-hover disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg transition-colors flex items-center gap-2"
          >
            <Send v-if="!chatStore.isStreaming" class="w-5 h-5" />
            <Loader2 v-else class="w-5 h-5 animate-spin" />
            <span>Enviar</span>
          </button>
        </form>
      </div>
    </div>
    
    <!-- Sources Panel -->
    <div
      v-if="showSourcesPanel"
      class="w-80 bg-surface border-l border-border flex flex-col"
    >
      <div class="p-4 border-b border-border flex items-center justify-between">
        <h3 class="font-semibold text-text flex items-center gap-2">
          <BookOpen class="w-5 h-5 text-primary" />
          Fontes
        </h3>
        <button @click="showSourcesPanel = false" class="text-text-muted hover:text-text">
          <X class="w-5 h-5" />
        </button>
      </div>
      <div class="flex-1 overflow-y-auto p-4 space-y-4">
        <div
          v-for="(source, index) in currentSources"
          :key="source.chunk_id"
          class="p-3 bg-background rounded-lg border border-border"
        >
          <div class="flex items-center justify-between mb-2">
            <span class="text-xs text-primary font-medium">
              Fonte {{ index + 1 }}
            </span>
            <span class="text-xs text-text-muted">
              {{ (source.similarity * 100).toFixed(1) }}%
            </span>
          </div>
          <p class="text-sm text-text-muted line-clamp-4">
            {{ source.content_preview }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'
import { marked } from 'marked'
import {
  MessageSquare,
  Plus,
  Trash2,
  Send,
  Loader2,
  BookOpen,
  X,
} from 'lucide-vue-next'
import { useChatStore } from '@/stores/chat'

const chatStore = useChatStore()
const messageInput = ref('')
const messagesContainer = ref(null)
const showSourcesPanel = ref(false)
const currentSources = ref([])

function renderMarkdown(content) {
  return marked.parse(content || '', { breaks: true })
}

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: 'short',
  })
}

async function createNewSession() {
  await chatStore.createSession()
}

async function selectSession(session) {
  await chatStore.selectSession(session)
}

async function deleteSession(sessionId) {
  if (confirm('Tem certeza que deseja excluir esta conversa?')) {
    await chatStore.deleteSession(sessionId)
  }
}

async function sendMessage() {
  const content = messageInput.value.trim()
  if (!content) return
  
  messageInput.value = ''
  
  try {
    await chatStore.sendMessage(content)
  } catch (e) {
    console.error('Error sending message:', e)
  }
}

function showSources(sources) {
  currentSources.value = sources
  showSourcesPanel.value = true
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

watch(
  () => [chatStore.messages.length, chatStore.streamingContent.length],
  scrollToBottom
)

onMounted(() => {
  chatStore.fetchSessions()
  if (!chatStore.currentSession) {
    chatStore.createSession()
  }
})
</script>
