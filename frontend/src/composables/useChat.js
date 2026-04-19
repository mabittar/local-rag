import { computed } from 'vue'
import { useChatStore } from '@/stores/chat'

export function useChat() {
  const store = useChatStore()

  return {
    sessions: computed(() => store.sessions),
    currentSession: computed(() => store.currentSession),
    messages: computed(() => store.messages),
    isStreaming: computed(() => store.isStreaming),
    streamingContent: computed(() => store.streamingContent),
    sources: computed(() => store.sources),
    fetchSessions: store.fetchSessions,
    createSession: store.createSession,
    selectSession: store.selectSession,
    sendMessage: store.sendMessage,
    deleteSession: store.deleteSession,
  }
}
