import { computed } from 'vue'
import { useDocumentsStore } from '@/stores/documents'

export function useDocuments() {
  const store = useDocumentsStore()

  return {
    documents: computed(() => store.documents),
    total: computed(() => store.total),
    isUploading: computed(() => store.isUploading),
    uploadProgress: computed(() => store.uploadProgress),
    fetchDocuments: store.fetchDocuments,
    uploadDocument: store.uploadDocument,
    deleteDocument: store.deleteDocument,
  }
}
