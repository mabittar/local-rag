import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

export function useAuth() {
  const store = useAuthStore()

  return {
    isAuthenticated: computed(() => store.isAuthenticated),
    token: computed(() => store.token),
    user: computed(() => store.user),
    login: store.login,
    logout: store.logout,
  }
}
