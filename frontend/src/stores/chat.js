import { defineStore } from 'pinia'
import api from '@/api/axios'

export const useChatStore = defineStore('chat', {
  state: () => ({
    sessions: [],
    currentSession: null,
    messages: [],
    isStreaming: false,
    streamingContent: '',
    sources: [],
  }),

  actions: {
    async fetchSessions() {
      const response = await api.get('/api/chat/sessions')
      this.sessions = response.data.items
    },

    async createSession(title = 'Nova Conversa') {
      const response = await api.post('/api/chat/sessions', { title })
      const session = response.data
      this.sessions.unshift(session)
      this.currentSession = session
      this.messages = []
      return session
    },

    async selectSession(session) {
      this.currentSession = session
      if (session) {
        const response = await api.get(`/api/chat/sessions/${session.id}/messages`)
        this.messages = response.data.messages
      } else {
        this.messages = []
      }
    },

    async sendMessage(content) {
      if (!this.currentSession) {
        await this.createSession()
      }

      this.messages.push({
        id: Date.now(),
        role: 'user',
        content,
        created_at: new Date().toISOString(),
      })

      this.isStreaming = true
      this.streamingContent = ''
      this.sources = []

      return new Promise((resolve, reject) => {
        const eventSource = new EventSource(
          `/api/chat/stream?session_id=${this.currentSession.id}&message=${encodeURIComponent(content)}`
        )

        eventSource.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data)
            
            if (data.type === 'token' && data.data) {
              this.streamingContent += data.data
            } else if (data.type === 'sources') {
              this.sources = data.sources || []
            } else if (data.type === 'done') {
              eventSource.close()
              this.messages.push({
                id: Date.now() + 1,
                role: 'assistant',
                content: this.streamingContent,
                sources: this.sources,
                created_at: new Date().toISOString(),
              })
              this.isStreaming = false
              resolve()
            }
          } catch (e) {
            console.error('Error parsing SSE data:', e)
          }
        }

        eventSource.onerror = () => {
          eventSource.close()
          this.isStreaming = false
          if (this.streamingContent) {
            this.messages.push({
              id: Date.now() + 1,
              role: 'assistant',
              content: this.streamingContent,
              sources: this.sources,
              created_at: new Date().toISOString(),
            })
          }
          reject(new Error('Connection error'))
        }
      })
    },

    async deleteSession(sessionId) {
      await api.delete(`/api/chat/sessions/${sessionId}`)
      this.sessions = this.sessions.filter((s) => s.id !== sessionId)
      if (this.currentSession?.id === sessionId) {
        this.currentSession = null
        this.messages = []
      }
    },
  },
})
