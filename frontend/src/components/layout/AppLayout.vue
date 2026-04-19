<template>
  <div class="min-h-screen bg-background flex">
    <AppSidebar />
    <div class="flex-1 flex flex-col min-w-0">
      <AppHeader />
      <main class="flex-1 overflow-auto p-6">
        <RouterView />
      </main>
    </div>
  </div>
</template>

<script setup>
import { RouterView } from 'vue-router'
import AppSidebar from './AppSidebar.vue'
import AppHeader from './AppHeader.vue'
</script>
