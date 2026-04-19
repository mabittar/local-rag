import { ref, onUnmounted } from 'vue'

export function useSSE() {
  const eventSource = ref(null)
  const isConnected = ref(false)
  const error = ref(null)

  function connect(url, onMessage, onError, onComplete) {
    disconnect()
    
    eventSource.value = new EventSource(url)
    isConnected.value = true
    error.value = null

    eventSource.value.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        onMessage?.(data)
      } catch (e) {
        console.error('Error parsing SSE data:', e)
      }
    }

    eventSource.value.onerror = (e) => {
      error.value = e
      onError?.(e)
      disconnect()
    }

    eventSource.value.addEventListener('done', () => {
      onComplete?.()
      disconnect()
    })
  }

  function disconnect() {
    if (eventSource.value) {
      eventSource.value.close()
      eventSource.value = null
      isConnected.value = false
    }
  }

  onUnmounted(() => {
    disconnect()
  })

  return {
    eventSource,
    isConnected,
    error,
    connect,
    disconnect,
  }
}
