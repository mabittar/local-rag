import { defineStore } from 'pinia'
import api from '@/api/axios'

export const useDocumentsStore = defineStore('documents', {
  state: () => ({
    documents: [],
    isUploading: false,
    uploadProgress: 0,
    total: 0,
  }),

  actions: {
    async fetchDocuments(skip = 0, limit = 20) {
      const response = await api.get('/api/documents', {
        params: { skip, limit },
      })
      this.documents = response.data.items
      this.total = response.data.total
    },

    async uploadDocument(file, onProgress) {
      const formData = new FormData()
      formData.append('file', file)

      this.isUploading = true
      this.uploadProgress = 0

      try {
        const response = await api.post('/api/documents/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          onUploadProgress: (progressEvent) => {
            if (progressEvent.total) {
              this.uploadProgress = Math.round(
                (progressEvent.loaded * 100) / progressEvent.total
              )
            }
            if (onProgress) {
              onProgress(this.uploadProgress)
            }
          },
        })

        await this.fetchDocuments()
        return response.data
      } finally {
        this.isUploading = false
        this.uploadProgress = 0
      }
    },

    async deleteDocument(documentId) {
      await api.delete(`/api/documents/${documentId}`)
      this.documents = this.documents.filter((d) => d.id !== documentId)
      this.total -= 1
    },
  },
})
