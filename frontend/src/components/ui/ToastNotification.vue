<script setup>
import { useToastStore } from '@/stores/toast'
const toast = useToastStore()

const icons = { success: '✅', error: '❌', warning: '⚠️', info: 'ℹ️' }
const colors = {
  success: 'bg-green-50 border-green-400 text-green-800',
  error:   'bg-red-50 border-red-400 text-red-800',
  warning: 'bg-amber-50 border-amber-400 text-amber-800',
  info:    'bg-blue-50 border-blue-400 text-blue-800',
}
</script>

<template>
  <Teleport to="body">
    <div class="fixed top-4 right-4 z-[9999] space-y-2 pointer-events-none">
      <TransitionGroup name="toast">
        <div v-for="t in toast.toasts" :key="t.id"
          :class="['flex items-center gap-3 px-4 py-3 rounded-xl border-l-4 shadow-lg max-w-sm pointer-events-auto', colors[t.type]]">
          <span class="text-lg shrink-0">{{ icons[t.type] }}</span>
          <p class="text-sm font-medium flex-1">{{ t.message }}</p>
          <button @click="toast.remove(t.id)" class="text-current opacity-60 hover:opacity-100 shrink-0 text-lg leading-none">×</button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<style scoped>
.toast-enter-active { transition: all 0.3s cubic-bezier(0.4,0,0.2,1); }
.toast-leave-active { transition: all 0.2s ease-in; }
.toast-enter-from  { opacity: 0; transform: translateX(100%); }
.toast-leave-to    { opacity: 0; transform: translateX(100%); }
</style>
