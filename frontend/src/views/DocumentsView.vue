<template>
  <div class="h-full flex flex-col">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <h2 class="text-xl font-bold text-text">Documentos</h2>
        <p class="text-text-muted text-sm mt-1">
          Gerencie seus documentos para consulta via RAG
        </p>
      </div>
      <div class="flex items-center gap-4">
        <span class="text-sm text-text-muted">
          {{ documentsStore.total }} documento(s)
        </span>
<label
      class="cursor-pointer flex items-center gap-2 px-4 py-2 bg-primary hover:bg-primary-hover text-white rounded-lg transition-colors"
      >
      <Upload class="w-4 h-4" />
      <span>Upload</span>
      <input
        type="file"
        accept=".pdf,.txt,.docx,.md"
        class="hidden"
        data-testid="file-upload-input"
        @change="handleFileSelect"
      />
    </label>
      </div>
    </div>
    
    <!-- Upload Dropzone -->
    <div
      @dragover.prevent
      @drop.prevent="handleDrop"
      @dragenter.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      :class="[
        'border-2 border-dashed rounded-xl p-8 mb-6 text-center transition-colors',
        isDragging
          ? 'border-primary bg-primary/10'
          : 'border-border hover:border-text-muted',
      ]"
    >
      <Upload class="w-12 h-12 text-text-muted mx-auto mb-4" />
      <p class="text-text-muted">
        Arraste e solte arquivos aqui, ou
        <label class="text-primary hover:underline cursor-pointer">
          clique para selecionar
<input
      type="file"
      accept=".pdf,.txt,.docx,.md"
      class="hidden"
      data-testid="file-upload-input-dropzone"
      @change="handleFileSelect"
    />
        </label>
      </p>
      <p class="text-text-muted text-sm mt-2">
        Formatos suportados: PDF, TXT, DOCX, MD (max 100MB)
      </p>
    </div>
    
    <!-- Upload Progress -->
    <div
      v-if="documentsStore.isUploading"
      class="mb-6 p-4 bg-surface border border-border rounded-lg"
    >
      <div class="flex items-center justify-between mb-2">
        <span class="text-sm text-text">Enviando...</span>
        <span class="text-sm text-text-muted">
          {{ documentsStore.uploadProgress }}%
        </span>
      </div>
      <div class="h-2 bg-surface-hover rounded-full overflow-hidden">
        <div
          class="h-full bg-primary transition-all duration-300"
          :style="{ width: `${documentsStore.uploadProgress}%` }"
        />
      </div>
    </div>
    
    <!-- Documents List -->
    <div class="flex-1 overflow-auto">
      <div v-if="documentsStore.documents.length === 0" class="text-center py-20">
        <FileText class="w-12 h-12 text-text-muted mx-auto mb-4" />
        <p class="text-text-muted">Nenhum documento encontrado</p>
        <p class="text-text-muted text-sm mt-1">
          Faça upload de documentos para começar
        </p>
      </div>
      
      <div v-else class="grid gap-4">
        <div
          v-for="doc in documentsStore.documents"
          :key="doc.id"
          class="p-4 bg-surface border border-border rounded-lg hover:border-primary/50 transition-colors group"
        >
          <div class="flex items-start justify-between">
            <div class="flex items-start gap-4">
              <div class="w-10 h-10 rounded-lg bg-primary/20 flex items-center justify-center">
                <FileText class="w-5 h-5 text-primary" />
              </div>
              <div>
                <h3 class="font-medium text-text">{{ doc.filename }}</h3>
                <div class="flex items-center gap-4 mt-1 text-sm text-text-muted">
                  <span>{{ formatFileSize(doc.file_size) }}</span>
                  <span>•</span>
                  <span>{{ doc.total_chunks }} chunks</span>
                  <span>•</span>
<span
              data-testid="status-badge"
              :class="[
                'px-2 py-0.5 rounded text-xs',
                doc.status === 'completed'
                  ? 'bg-success/20 text-success'
                  : doc.status === 'processing'
                  ? 'bg-warning/20 text-warning'
                  : 'bg-error/20 text-error',
              ]"
            >
              {{ doc.status }}
            </span>
                </div>
              </div>
            </div>
<button
          @click="deleteDocument(doc.id)"
          data-testid="delete-document"
          class="p-2 text-text-muted hover:text-error hover:bg-error/10 rounded-lg transition-colors opacity-0 group-hover:opacity-100"
          >
              <Trash2 class="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Error Toast -->
    <div
      v-if="error"
      class="fixed bottom-6 right-6 p-4 bg-error/90 text-white rounded-lg shadow-lg flex items-center gap-3"
    >
      <AlertCircle class="w-5 h-5" />
      <span>{{ error }}</span>
      <button @click="error = ''" class="text-white/70 hover:text-white">
        <X class="w-4 h-4" />
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Upload, FileText, Trash2, AlertCircle, X } from 'lucide-vue-next'
import { useDocumentsStore } from '@/stores/documents'

const documentsStore = useDocumentsStore()
const isDragging = ref(false)
const error = ref('')

function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

async function handleFileSelect(event) {
  const file = event.target.files?.[0]
  if (!file) return
  await uploadFile(file)
  event.target.value = ''
}

async function handleDrop(event) {
  isDragging.value = false
  const file = event.dataTransfer.files?.[0]
  if (!file) return
  await uploadFile(file)
}

async function uploadFile(file) {
  const allowedTypes = ['pdf', 'txt', 'docx', 'md']
  const extension = file.name.split('.').pop()?.toLowerCase()
  
  if (!allowedTypes.includes(extension)) {
    error.value = 'Formato não suportado. Use: PDF, TXT, DOCX, MD'
    setTimeout(() => (error.value = ''), 5000)
    return
  }
  
  if (file.size > 100 * 1024 * 1024) {
    error.value = 'Arquivo muito grande. Tamanho máximo: 100MB'
    setTimeout(() => (error.value = ''), 5000)
    return
  }
  
  error.value = ''
  
  try {
    await documentsStore.uploadDocument(file)
  } catch (e) {
    error.value = e.response?.data?.detail || 'Erro ao fazer upload'
    setTimeout(() => (error.value = ''), 5000)
  }
}

async function deleteDocument(id) {
  if (confirm('Tem certeza que deseja excluir este documento?')) {
    await documentsStore.deleteDocument(id)
  }
}

onMounted(() => {
  documentsStore.fetchDocuments()
})
</script>
