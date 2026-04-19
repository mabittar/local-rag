import { defineStore } from 'pinia'
import api from '@/api/axios'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token'),
    isAuthenticated: !!localStorage.getItem('token'),
  }),

  actions: {
    async login(credentials) {
      const response = await api.post('/api/auth/login', credentials)
      this.token = response.data.access_token
      this.isAuthenticated = true
      localStorage.setItem('token', this.token)
      return response.data
    },

    logout() {
      this.user = null
      this.token = null
      this.isAuthenticated = false
      localStorage.removeItem('token')
    },
  },
})
